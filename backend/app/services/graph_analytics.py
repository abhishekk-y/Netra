"""Explainable graph/behavior analytics over observed flows, without network probes."""
from __future__ import annotations

from collections import Counter, defaultdict, deque
from datetime import datetime, timezone
from math import log2
from statistics import mean, median, pstdev
from typing import Any


def instant(value: str | datetime) -> datetime:
    parsed = value if isinstance(value, datetime) else datetime.fromisoformat(value.replace("Z", "+00:00"))
    return parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed.astimezone(timezone.utc)


def build_graph(hosts: list[dict], flows: list[dict], at: str | None = None, since: str | None = None) -> dict:
    """Reconstruct a logical communication graph. Never infer unobserved switches."""
    upper, lower = instant(at) if at else None, instant(since) if since else None
    if upper and lower and lower > upper:
        raise ValueError("since must not be later than at")
    selected = [f for f in flows if (not upper or instant(f["timestamp"]) <= upper) and (not lower or instant(f["timestamp"]) >= lower)]
    by_ip = {h["ip"]: h for h in hosts}
    nodes: dict[str, dict] = {}
    links: dict[tuple[str, str], dict] = {}
    for flow in sorted(selected, key=lambda f: instant(f["timestamp"])):
        for ip in (flow["srcIp"], flow["dstIp"]):
            host = by_ip.get(ip, {})
            node = nodes.setdefault(ip, {"id": host.get("id", ip), "ip": ip, "label": host.get("hostname") or ip,
                "risk": 0, "firstSeen": flow["timestamp"], "lastSeen": flow["timestamp"], "flowIds": []})
            node["lastSeen"] = flow["timestamp"]
            node["risk"] = max(node["risk"], flow.get("riskScore", 0))
            node["flowIds"].append(flow["id"])
        source, target = flow["srcIp"], flow["dstIp"]
        edge = links.setdefault((source, target), {"id": f"{source}>{target}", "source": source, "target": target,
            "bytes": 0, "packets": 0, "flowCount": 0, "risk": 0, "protocols": set(), "ports": set(),
            "flowIds": [], "communityIds": set(), "firstSeen": flow["timestamp"], "lastSeen": flow["timestamp"]})
        edge["bytes"] += flow.get("bytes", 0)
        edge["packets"] += flow.get("packets", 0)
        edge["flowCount"] += 1
        edge["risk"] = max(edge["risk"], flow.get("riskScore", 0))
        edge["protocols"].add(flow["protocol"])
        edge["ports"].add(flow["dstPort"])
        edge["flowIds"].append(flow["id"])
        if flow.get("communityId"):
            edge["communityIds"].add(flow["communityId"])
        edge["lastSeen"] = flow["timestamp"]
    for edge in links.values():
        for key in ("protocols", "ports", "communityIds"):
            edge[key] = sorted(edge[key])
        edge["evidence"] = "Observed source-to-destination flow records; not a physical routing path."
    return {"nodes": list(nodes.values()), "edges": list(links.values()), "at": at, "since": since,
        "flowCount": len(selected), "semantics": "observed-directed-communications",
        "limitations": "Historical risk is reconstructed from recorded flow risk. Names use current inventory; no historical physical-device claims."}


def communication_path(graph: dict, source: str, destination: str) -> dict:
    adjacency: dict[str, list[dict]] = defaultdict(list)
    for edge in graph["edges"]:
        adjacency[edge["source"]].append(edge)
    known = {n["ip"] for n in graph["nodes"]}
    if source not in known or destination not in known:
        raise ValueError("Both endpoints must have observed flow evidence")
    queue = deque([(source, [source], [])])
    visited = {source}
    while queue:
        current, nodes, evidence = queue.popleft()
        if current == destination:
            return {"found": True, "nodes": nodes, "edges": evidence, "hops": len(evidence),
                "semantics": "Shortest chain of observed directed communications, not a packet route or proof of exploitability."}
        for edge in sorted(adjacency[current], key=lambda e: e["target"]):
            if edge["target"] not in visited:
                visited.add(edge["target"])
                queue.append((edge["target"], nodes + [edge["target"]], evidence + [edge]))
    return {"found": False, "nodes": [], "edges": [], "hops": None, "semantics": "No observed directed communication chain."}


def blast_radius(graph: dict, source: str, max_hops: int = 2) -> dict:
    if not 1 <= max_hops <= 5:
        raise ValueError("max_hops must be between 1 and 5")
    if source not in {n["ip"] for n in graph["nodes"]}:
        raise ValueError("Source must have observed flow evidence")
    adjacency: dict[str, list[dict]] = defaultdict(list)
    for edge in graph["edges"]:
        adjacency[edge["source"]].append(edge)
    seen = {source}
    queue = deque([(source, 0)])
    exposed = []
    while queue:
        current, depth = queue.popleft()
        if depth >= max_hops:
            continue
        for edge in sorted(adjacency[current], key=lambda e: e["target"]):
            target = edge["target"]
            if target not in seen:
                seen.add(target)
                exposed.append({"ip": target, "hops": depth + 1, "via": current, "flowIds": edge["flowIds"]})
                queue.append((target, depth + 1))
    return {"source": source, "maxHops": max_hops, "directCount": sum(x["hops"] == 1 for x in exposed),
        "totalCount": len(exposed), "assets": exposed,
        "semantics": "Communication exposure estimate. Past traffic does not establish current firewall reachability or compromise."}


def topology_diff(before: dict, after: dict) -> dict:
    bn, an = {n["ip"]: n for n in before["nodes"]}, {n["ip"]: n for n in after["nodes"]}
    be, ae = {e["id"]: e for e in before["edges"]}, {e["id"]: e for e in after["edges"]}
    changes = []
    for key in sorted(be.keys() & ae.keys()):
        fields = {field: {"before": be[key][field], "after": ae[key][field]} for field in ("risk", "ports", "protocols", "flowCount", "bytes") if be[key][field] != ae[key][field]}
        if fields:
            changes.append({"id": key, "changes": fields})
    return {"addedNodes": [an[k] for k in sorted(an.keys() - bn.keys())],
        "removedNodes": [bn[k] for k in sorted(bn.keys() - an.keys())],
        "addedEdges": [ae[k] for k in sorted(ae.keys() - be.keys())],
        "removedEdges": [be[k] for k in sorted(be.keys() - ae.keys())], "changedEdges": changes,
        "semantics": "Difference between observed windows. Absence in a window does not prove a device went offline."}


def behavior_summary(flows: list[dict[str, Any]]) -> dict:
    """Descriptive periodicity and robust distribution shift, never an attack verdict."""
    pairs: dict[tuple, list[dict]] = defaultdict(list)
    sources: dict[str, list[dict]] = defaultdict(list)
    for flow in flows:
        pairs[(flow["srcIp"], flow["dstIp"], flow["dstPort"], flow["protocol"])].append(flow)
        sources[flow["srcIp"]].append(flow)
    periodicity = []
    for (src, dst, port, protocol), group in sorted(pairs.items()):
        ordered = sorted(group, key=lambda f: instant(f["timestamp"]))
        if len(ordered) < 6:
            continue
        times = [instant(f["timestamp"]).timestamp() for f in ordered]
        intervals = [b - a for a, b in zip(times, times[1:])]
        average = mean(intervals)
        if average <= 0:
            continue
        cv = pstdev(intervals) / average
        periodicity.append({"source": src, "destination": dst, "port": port, "protocol": protocol,
            "periodSeconds": round(average, 3), "intervalCv": round(cv, 4), "regularityScore": round(max(0, 1 - cv), 4),
            "sampleCount": len(ordered), "flowIds": [f["id"] for f in ordered],
            "interpretation": "Regular traffic can be legitimate scheduled work. This score is not a malware probability."})
    profiles = []
    for src, group in sorted(sources.items()):
        ordered = sorted(group, key=lambda f: instant(f["timestamp"]))
        counts = Counter(f["dstIp"] for f in ordered)
        entropy = -sum((c / len(ordered)) * log2(c / len(ordered)) for c in counts.values())
        profile: dict = {"source": src, "flowCount": len(ordered), "uniquePeers": len(counts),
            "uniquePorts": len({f["dstPort"] for f in ordered}), "peerEntropyBits": round(entropy, 4),
            "totalBytes": sum(f.get("bytes", 0) for f in ordered), "baselineStatus": "insufficient-history"}
        if len(ordered) >= 20:
            split = len(ordered) // 2
            baseline, recent = ordered[:split], ordered[split:]
            values = [f.get("bytes", 0) for f in baseline]
            center = median(values)
            mad = median(abs(x - center) for x in values)
            recent_center = median(f.get("bytes", 0) for f in recent)
            # Zero MAD cannot support a meaningful standardized effect size.
            score = abs(recent_center - center) / (1.4826 * mad) if mad else None
            profile.update({"baselineStatus": "descriptive-temporal-split", "baselineSamples": len(baseline),
                "recentSamples": len(recent), "baselineMedianBytes": center, "recentMedianBytes": recent_center,
                "medianAbsoluteDeviation": mad, "robustShiftScore": round(score, 3) if score is not None else None,
                "newPeers": sorted({f["dstIp"] for f in recent} - {f["dstIp"] for f in baseline}),
                "baselineFlowIds": [f["id"] for f in baseline], "recentFlowIds": [f["id"] for f in recent]})
        profiles.append(profile)
    return {"periodicity": sorted(periodicity, key=lambda p: p["regularityScore"], reverse=True), "sourceProfiles": profiles,
        "method": "Interval coefficient of variation; chronological half-split median/MAD; Shannon peer entropy.",
        "limitations": "Descriptive evidence only. No learned baseline, causal inference, or calibrated attack probability."}
