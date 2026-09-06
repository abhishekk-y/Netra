"""Flow adapters and content-addressed evidence for local sensor imports."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import uuid
from .normalizer.event_normalizer import EventNormalizer
from .zeek.log_watcher import ZeekLogWatcher


def preserve_evidence(path, evidence_dir):
    """Store a verified copy and create a manifest once; never overwrite evidence."""
    path, directory = Path(path), Path(evidence_dir)
    directory.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    sha256 = digest.hexdigest()
    destination = directory / (sha256 + path.suffix.lower())
    try:
        with path.open("rb") as source, destination.open("xb") as target:
            shutil.copyfileobj(source, target)
    except FileExistsError:
        pass
    stored_digest = hashlib.sha256()
    with destination.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            stored_digest.update(block)
    if stored_digest.hexdigest() != sha256:
        raise ValueError("Evidence changed during import or stored evidence is corrupt")
    manifest_path = directory / (sha256 + ".json")
    manifest = {"sha256": sha256, "sizeBytes": destination.stat().st_size,
                "originalName": path.name, "storedName": destination.name,
                "importedAt": datetime.now(timezone.utc).isoformat()}
    try:
        with manifest_path.open("x", encoding="utf-8") as stream:
            json.dump(manifest, stream, indent=2)
    except FileExistsError:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("sha256") != sha256:
            raise ValueError("Stored evidence manifest does not match evidence")
    return manifest


def packet_flow(packet, source="pcap-import"):
    """Represent each observed IP packet as a flow record without inferred bytes."""
    from scapy.layers.inet import IP, TCP, UDP
    from scapy.layers.inet6 import IPv6
    network = packet.getlayer(IP) or packet.getlayer(IPv6)
    if network is None:
        return None
    transport = packet.getlayer(TCP) or packet.getlayer(UDP)
    protocol = "TCP" if packet.haslayer(TCP) else "UDP" if packet.haslayer(UDP) else "ICMP" if getattr(network, "proto", getattr(network, "nh", 0)) in (1, 58) else "OTHER"
    sport, dport = (int(transport.sport), int(transport.dport)) if transport else (0, 0)
    return {"srcIp": network.src, "dstIp": network.dst,
            "srcPort": int(transport.sport) if transport else 0,
            "dstPort": int(transport.dport) if transport else 0,
            "protocol": protocol, "packets": 1, "bytes": len(packet),
            "duration": 0.0, "timestamp": datetime.fromtimestamp(float(packet.time), timezone.utc).isoformat(),
            "source": source,
            "eventId": str(uuid.uuid4()),
            "communityId": EventNormalizer.calculate_community_id(network.src, network.dst, sport, dport, protocol) or None,
            "rawSource": "pcap"}


def read_pcap(path):
    """Stream PCAP or PCAPNG, aggregate directional 5-tuples in bounded chunks."""
    from scapy.utils import PcapReader
    flows = {}
    with PcapReader(str(path)) as packets:
        for packet in packets:
            flow = packet_flow(packet)
            if flow is None:
                continue
            key = tuple(flow[k] for k in ("srcIp", "dstIp", "srcPort", "dstPort", "protocol"))
            if key in flows:
                existing = flows[key]
                existing["packets"] += 1
                existing["bytes"] += flow["bytes"]
                existing["duration"] = max(existing["duration"],
                    (datetime.fromisoformat(flow["timestamp"]) - datetime.fromisoformat(existing["timestamp"])).total_seconds())
            else:
                flows[key] = flow
            if len(flows) >= 1000:
                yield from flows.values()
                flows.clear()
    yield from flows.values()


def read_logs(path, kind):
    normalizer = EventNormalizer("file-import")
    watcher = ZeekLogWatcher(str(Path(path).parent)) if kind == "zeek" else None
    with Path(path).open(encoding="utf-8", errors="replace") as stream:
        for number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            if kind == "zeek":
                raw = watcher._parse_line("conn.log", line)
                if not raw:
                    if line.startswith("#"):
                        continue
                    raise ValueError(f"Invalid Zeek record at line {number}")
                event = normalizer.normalize_zeek(raw)
            else:
                try:
                    raw = json.loads(line)
                except ValueError as exc:
                    raise ValueError(f"Invalid Suricata JSON at line {number}") from exc
                event = normalizer.normalize_suricata(raw)
            if event is None:
                raise ValueError(f"Invalid normalized event at line {number}")
            if not event.source_ip or not event.dest_ip:
                continue
            if kind == "zeek":
                def numeric(key):
                    value = raw.get(key, 0)
                    return 0 if value in (None, "", "-") else float(value)
                packets = numeric("orig_pkts") + numeric("resp_pkts")
                byte_count = numeric("orig_ip_bytes") + numeric("resp_ip_bytes")
                if not byte_count:
                    byte_count = numeric("orig_bytes") + numeric("resp_bytes")
                duration = numeric("duration")
            else:
                # Only Suricata flow summaries have traffic counters; alert/DNS
                # records alone must not invent packet or byte measurements.
                if raw.get("event_type") != "flow":
                    continue
                details = raw.get("flow", {})
                packets = details.get("pkts_toserver", 0) + details.get("pkts_toclient", 0)
                byte_count = details.get("bytes_toserver", 0) + details.get("bytes_toclient", 0)
                duration = float(details.get("age", 0))
            yield {"srcIp": event.source_ip, "dstIp": event.dest_ip,
                   "srcPort": event.source_port or 0, "dstPort": event.dest_port or 0,
                   "protocol": (event.protocol or "OTHER").upper(), "packets": int(packets),
                   "bytes": int(byte_count), "duration": duration,
                   "timestamp": event.timestamp.isoformat(), "source": kind + "-import",
                   "eventId": event.event_id, "communityId": event.community_id,
                   "rawSource": kind, "sessionUid": str(raw.get("uid", raw.get("flow_id", ""))) or None}


def packet_summaries(path, offset=0, limit=100):
    """Paginate actual packets for a PCAP explorer; decoded payload is not invented."""
    from scapy.utils import PcapReader
    if offset < 0 or not 1 <= limit <= 1000:
        raise ValueError("offset must be nonnegative; limit must be 1..1000")
    result = []
    with PcapReader(str(path)) as packets:
        for index, packet in enumerate(packets):
            if index < offset:
                continue
            if len(result) >= limit:
                break
            flow = packet_flow(packet)
            result.append({"packetNumber": index + 1, "timestamp": datetime.fromtimestamp(float(packet.time), timezone.utc).isoformat(),
                           "capturedLength": len(packet), "wireLength": getattr(packet, "wirelen", None),
                           "summary": packet.summary(), "flow": flow, "hex": bytes(packet).hex()})
    return result
