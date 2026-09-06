"""SQLite workbench. Detection and forecasting here are transparent heuristics.

Historical packet timestamps and ingestion timestamps are distinct. No telemetry
is fabricated unless NETRA_SEED_DEMO=true is explicitly configured.
"""
import json
import os
import re
import shutil
import sqlite3
from collections import Counter
from datetime import datetime, timedelta, timezone
from ipaddress import ip_address
from pathlib import Path
from threading import RLock
from uuid import uuid4, uuid5, NAMESPACE_DNS
from fastapi import HTTPException

def now():
    return datetime.now(timezone.utc).isoformat()

def host_id(ip):
    return str(uuid5(NAMESPACE_DNS, f"netra:{ip}"))

class Store:
    def __init__(self, path=None, seed_demo=None):
        self.path = str(path or os.getenv("NETRA_DB_PATH", str(Path(__file__).resolve().parents[1] / "data" / "netra.db")))
        if self.path != ":memory:":
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self.lock = RLock()
        self.db = sqlite3.connect(self.path, check_same_thread=False)
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("CREATE TABLE IF NOT EXISTS entities (kind TEXT NOT NULL, id TEXT NOT NULL, payload TEXT NOT NULL, PRIMARY KEY(kind,id))")
        self.db.commit()
        enabled = seed_demo if seed_demo is not None else os.getenv("NETRA_SEED_DEMO", "false").lower() == "true"
        if not self.all("settings"):
            with self.db:
                self.put("settings", {"id": "current", "profile": "STANDARD", "retentionDays": 30, "autoRefresh": True, "demoMode": enabled})
        if enabled and not self.all("flows") and not self.all("metadata"):
            self.seed()
        self.prune()

    def close(self):
        self.db.close()

    def ping(self):
        with self.lock:
            self.db.execute("SELECT 1").fetchone()

    def all(self, kind):
        with self.lock:
            return [json.loads(row[0]) for row in self.db.execute("SELECT payload FROM entities WHERE kind=? ORDER BY rowid DESC", (kind,))]

    def put(self, kind, value):
        self.db.execute("INSERT INTO entities(kind,id,payload) VALUES (?,?,?) ON CONFLICT(kind,id) DO UPDATE SET payload=excluded.payload", (kind, value["id"], json.dumps(value)))

    def get(self, kind, entity_id):
        with self.lock:
            row = self.db.execute("SELECT payload FROM entities WHERE kind=? AND id=?", (kind, entity_id)).fetchone()
        if row is None:
            raise HTTPException(404, f"{kind.rstrip('s').capitalize()} not found")
        return json.loads(row[0])

    def page(self, kind, page=1, page_size=100, search=""):
        records = self.all(kind)
        if search:
            records = [item for item in records if search.casefold() in json.dumps(item).casefold()]
        return {"data": records[(page-1)*page_size:page*page_size], "total": len(records), "page": page, "pageSize": page_size}

    def settings(self):
        return self.get("settings", "current")

    def audit(self, action, entity_id, before, after):
        self.put("audit", {"id": str(uuid4()), "timestamp": now(), "actor": "local-operator", "action": action, "entityId": entity_id, "before": before, "after": after})

    def update_settings(self, update):
        with self.lock, self.db:
            previous = self.settings()
            record = {**previous, **update}
            self.put("settings", record)
            self.audit("settings.update", "current", previous, record)
        self.prune()
        return record

    def prune(self):
        # Retain imported historical captures for N days after ingestion.
        cutoff = (datetime.now(timezone.utc) - timedelta(days=self.settings()["retentionDays"])).isoformat()
        with self.lock, self.db:
            for kind in ("flows", "alerts"):
                for record in self.all(kind):
                    if record.get("ingestedAt", record["timestamp"]) < cutoff:
                        self.db.execute("DELETE FROM entities WHERE kind=? AND id=?", (kind, record["id"]))

    def update_status(self, kind, entity_id, status):
        with self.lock, self.db:
            record = self.get(kind, entity_id)
            old_status = record["status"]
            record.update(status=status, operatorUpdatedAt=now())
            self.put(kind, record)
            self.audit(f"{kind}.status", entity_id, old_status, status)
            return record

    def ingest(self, inputs):
        result = {"accepted": len(inputs), "alertsCreated": 0, "incidentsCreated": 0, "flows": []}
        with self.lock, self.db:
            recent = self.all("flows")
            hosts = {host["ip"]: host for host in self.all("hosts")}
            for entry in inputs:
                timestamp = datetime.fromisoformat(entry.get("timestamp", now()).replace("Z", "+00:00")).astimezone(timezone.utc).isoformat()
                flow = {**entry, "id": str(uuid4()), "timestamp": timestamp, "ingestedAt": now(), "riskScore": 5, "anomalyScore": .05,
                        "appProtocol": {22:"SSH", 53:"DNS", 80:"HTTP", 443:"TLS", 445:"SMB", 3389:"RDP"}.get(entry["dstPort"], entry["protocol"]),
                        "source": entry.get("source", "ingested"), "synthetic": entry.get("source", "").startswith("demo"),
                        "protocolEvidence": "Destination-port inference; payload protocol not verified"}
                rule = None
                moment = datetime.fromisoformat(timestamp)
                same_source = [f for f in recent if f["srcIp"] == flow["srcIp"] and 0 <= (moment-datetime.fromisoformat(f["timestamp"])).total_seconds() <= 300]
                ports = {f["dstPort"] for f in same_source} | {flow["dstPort"]}
                if len(ports) >= 8:
                    rule = ("Reconnaissance", "Port fan-out: at least 8 destination ports within 5 minutes", "high", 72, "Discovery", "T1046")
                if flow["dstPort"] in (445, 3389) and flow["packets"] >= 20:
                    rule = ("Lateral Movement", "Remote service activity on SMB/RDP", "high", 78, "Lateral Movement", "T1021")
                if flow["bytes"] >= 5_000_000 and not ip_address(flow["dstIp"]).is_private:
                    rule = ("Exfiltration", "Large outbound transfer to an external address", "critical", 92, "Exfiltration", "T1041")
                if flow["duration"] > 0 and flow["packets"] >= 1000 and flow["packets"] / flow["duration"] >= 10000:
                    rule = ("Impact", "High packet rate: at least 10,000 packets per second", "critical", 95, "Impact", "T1498")
                if rule:
                    flow.update(attackType=rule[0], riskScore=rule[3], anomalyScore=rule[3]/100, detectionReason=rule[1])
                for ip, port in ((flow["srcIp"], flow["srcPort"]), (flow["dstIp"], flow["dstPort"])):
                    host = hosts.get(ip) or {"id": host_id(ip), "ip": ip, "hostname": ip, "deviceType": "unknown", "criticality": "medium", "firstSeen": timestamp, "lastSeen": timestamp, "riskScore": 0, "openPorts": [], "protocols": [], "synthetic": flow["synthetic"], "identityConfidence": 1.0, "deviceTypeConfidence": 0, "evidence": "Observed IP in ingested flow; device role unknown", "portSemantics": "Observed destination ports, not verified listening services"}
                    host.update(firstSeen=min(host["firstSeen"], timestamp), lastSeen=max(host["lastSeen"], timestamp), riskScore=max(host["riskScore"], flow["riskScore"]), synthetic=host["synthetic"] and flow["synthetic"])
                    if ip == flow["dstIp"] and port and port not in host["openPorts"]:
                        host["openPorts"].append(port)
                    if flow["protocol"] not in host["protocols"]:
                        host["protocols"].append(flow["protocol"])
                    hosts[ip] = host
                    self.put("hosts", host)
                self.put("flows", flow)
                recent.append(flow)
                result["flows"].append(flow)
                if rule:
                    self.match_forecasts(flow)
                    alert = {"id": str(uuid4()), "timestamp": timestamp, "ingestedAt": flow["ingestedAt"], "severity": rule[2], "source": "heuristic-rules", "signature": rule[1], "srcIp": flow["srcIp"], "dstIp": flow["dstIp"], "protocol": flow["protocol"], "mitreTactic": rule[4], "mitreTechnique": rule[5], "confidence": rule[3]/100, "status": "new", "flowId": flow["id"], "synthetic": flow["synthetic"], "confidenceMeaning": "Rule priority score, not a calibrated probability. Legitimate activity can match."}
                    self.put("alerts", alert)
                    result["alertsCreated"] += 1
                    incidents = [i for i in self.all("incidents") if i["sourceIp"] == flow["srcIp"] and i["status"] in ("active", "investigating") and abs((moment-datetime.fromisoformat(i["updatedAt"])).total_seconds()) <= 1800]
                    incident = incidents[0] if incidents else {"id": str(uuid4()), "title": f"Suspicious activity from {flow['srcIp']}", "status": "active", "severity": rule[2], "stage": rule[0], "affectedHosts": [], "createdAt": timestamp, "updatedAt": timestamp, "sourceIp": flow["srcIp"], "alertIds": [], "synthetic": flow["synthetic"]}
                    if not incidents:
                        result["incidentsCreated"] += 1
                    if timestamp >= incident["updatedAt"]:
                        incident.update(stage=rule[0], updatedAt=timestamp)
                    incident["synthetic"] = incident["synthetic"] and flow["synthetic"]
                    if rule[2] == "critical":
                        incident["severity"] = "critical"
                    incident["affectedHosts"] = sorted(set(incident["affectedHosts"] + [host_id(flow["srcIp"]), host_id(flow["dstIp"])]))
                    incident["alertIds"].append(alert["id"])
                    self.put("incidents", incident)
                    snapshot = self.build_forecast(incident)
                    self.put("forecasts", snapshot)
            self.audit("flows.ingest", "batch", None, {"accepted": len(inputs), "sources": sorted({f["source"] for f in result["flows"]})})
        self.prune()
        return result

    def match_forecasts(self, flow):
        for forecast in self.all("forecasts"):
            if forecast.get("outcome") or forecast["sourceIp"] != flow["srcIp"]:
                continue
            if flow["timestamp"] <= forecast["evidenceThrough"] or flow["ingestedAt"] <= forecast["timestamp"]:
                continue
            if flow["attackType"] not in [s["stage"] for s in forecast["nextStages"]]:
                continue
            elapsed = (datetime.fromisoformat(flow["ingestedAt"])-datetime.fromisoformat(forecast["timestamp"])).total_seconds()
            forecast["outcome"] = {"flowId": flow["id"], "observedStage": flow["attackType"], "observedAt": flow["ingestedAt"], "eventTimestamp": flow["timestamp"], "leadTimeSeconds": elapsed, "evaluation": "Later ingested rule match, not ground truth or model accuracy", "synthetic": flow["synthetic"]}
            self.put("forecasts", forecast)

    def host_detail(self, entity_id):
        host = self.get("hosts", entity_id)
        return {**host, "activeAlerts": [a for a in self.all("alerts") if host["ip"] in (a["srcIp"], a["dstIp"]) and a["status"] != "resolved"], "recentFlows": [f for f in self.all("flows") if host["ip"] in (f["srcIp"], f["dstIp"])][:100]}

    def incident_detail(self, entity_id):
        incident = self.get("incidents", entity_id)
        alerts = [a for a in self.all("alerts") if a["id"] in incident["alertIds"]]
        return {**incident, "alerts": alerts, "flows": [f for f in self.all("flows") if f["id"] in {a["flowId"] for a in alerts}], "forecasts": [f for f in self.all("forecasts") if f["incidentId"] == entity_id], "reportGeneratedAt": now(), "method": "Rule-derived investigation evidence; not proof of compromise"}

    def summary(self):
        incidents = [i for i in self.all("incidents") if i["status"] in ("active", "investigating")]
        alerts = [a for a in self.all("alerts") if a["status"] != "resolved"]
        flows = self.all("flows")
        return {"activeIncidents": len(incidents), "criticalAlerts": sum(a["severity"] == "critical" for a in alerts), "forecastRiskLevel": "critical" if any(i["severity"] == "critical" for i in incidents) else "high" if incidents else "low", "totalHosts": len(self.all("hosts")), "totalFlows": len(flows), "dataMode": "empty" if not flows else "synthetic-demo" if all(f["synthetic"] for f in flows) else "mixed" if any(f["synthetic"] for f in flows) else "ingested"}

    def topology(self):
        hosts = self.all("hosts")
        active_ips = {ip for a in self.all("alerts") if a["status"] != "resolved" for ip in (a["srcIp"], a["dstIp"])}
        edges = {}
        for flow in self.all("flows"):
            src, dst = host_id(flow["srcIp"]), host_id(flow["dstIp"])
            key = f"{src}:{dst}"
            edge = edges.setdefault(key, {"data": {"id": key, "source": src, "target": dst, "weight": 0, "risk": 0, "isAttackPath": False, "flowIds": [], "evidence": "Observed directed flow", "confidence": 1.0, "firstSeen": flow["timestamp"], "lastSeen": flow["timestamp"]}})["data"]
            edge.update(weight=edge["weight"] + flow["bytes"], risk=max(edge["risk"], flow["riskScore"]), isAttackPath=edge["isAttackPath"] or flow["riskScore"] >= 70, firstSeen=min(edge["firstSeen"], flow["timestamp"]), lastSeen=max(edge["lastSeen"], flow["timestamp"]))
            edge["flowIds"].append(flow["id"])
        return {"nodes": [{"data": {"id": h["id"], "label": h["hostname"], "type": h["deviceType"], "risk": h["riskScore"], "hasAlert": h["ip"] in active_ips}} for h in hosts], "edges": list(edges.values()), "semantics": "Observed directed communication, not physical wiring. Port-derived roles are unverified."}

    def build_forecast(self, incident=None):
        stage = incident["stage"] if incident else "No active incident"
        transitions = {"Reconnaissance": [("Initial Access", .55), ("Lateral Movement", .30), ("Impact", .15)], "Lateral Movement": [("Collection", .50), ("Exfiltration", .35), ("Impact", .15)], "Exfiltration": [("Impact", .60), ("Persistence", .40)], "Impact": [("Persistence", .55), ("Exfiltration", .45)]}
        targets = sorted(self.all("hosts"), key=lambda h: h["riskScore"], reverse=True)[:5] if incident else []
        total = sum(h["riskScore"] + 1 for h in targets) or 1
        return {"id": str(uuid4()) if incident else "heuristic-idle", "timestamp": now(), "evidenceThrough": incident["updatedAt"] if incident else None, "incidentId": incident["id"] if incident else None, "sourceIp": incident["sourceIp"] if incident else None, "currentStage": stage, "stageConfidence": .7 if incident else 0, "nextStages": [{"stage": s, "probability": p} for s,p in transitions.get(stage, [])], "targetPredictions": [{"hostId": h["id"], "ip": h["ip"], "probability": round((h["riskScore"]+1)/total, 4)} for h in targets], "method": "heuristic-transition-rules", "calibrated": False, "synthetic": incident["synthetic"] if incident else False, "explanation": "Fixed stage weights and normalized historical host risk are investigation priorities, not validated attack probabilities. Snapshots precede later ingestion; outcome lead time uses ingestion wall clock."}

    def forecast(self):
        active = {i["id"] for i in self.all("incidents") if i["status"] in ("active", "investigating")}
        forecasts = [f for f in self.all("forecasts") if f["incidentId"] in active]
        return forecasts[0] if forecasts else self.build_forecast()

    def health(self):
        self.ping()
        import psutil
        disk_path = str(Path(self.path).resolve().parent) if self.path != ":memory:" else str(Path.cwd())
        usage = shutil.disk_usage(disk_path)
        return {"status": "degraded", "components": {"database": "up", "capture": "down", "inference": "up"}, "metrics": {"cpu": psutil.cpu_percent(), "memory": psutil.virtual_memory().percent, "disk": round(usage.used/usage.total*100, 1)}, "mode": "local", "inferenceMethod": "heuristic-rules", "captureAvailable": False, "message": "API and heuristic analysis available. Capture is an external CLI; continuous sensor heartbeat is not implemented.", "database": "SQLite", "authentication": "bearer-token" if os.getenv("NETRA_API_TOKEN") else "none-local-only"}

    def telemetry(self):
        health = self.health()
        cutoff = datetime.now(timezone.utc) - timedelta(seconds=60)
        recent = [f for f in self.all("flows") if datetime.fromisoformat(f["ingestedAt"]) >= cutoff]
        return {"packetsPerSec": round(sum(f["packets"] for f in recent)/60, 1), "flowsPerSec": round(len(recent)/60, 2), "hostsCount": len(self.all("hosts")), "activeConnections": len(recent), "sensorStatus": "degraded", "captureDropPercent": 0, "cpuUsage": health["metrics"]["cpu"], "ramUsage": health["metrics"]["memory"], "diskUsage": health["metrics"]["disk"], "captureAvailable": False, "rateMeaning": "Ingested records in last minute; not live capture counters"}

    def hunt(self, query):
        records = self.all("flows")
        if query.strip():
            # Never execute Python, SQL or shell text.
            if re.search(r"==|!=|>=|<=|>|<", query):
                for clause in re.split(r"\s+and\s+", query.strip(), flags=re.I):
                    match = re.fullmatch(r"(srcIp|dstIp|srcPort|dstPort|protocol|appProtocol|bytes|packets|duration|riskScore|attackType)\s*(==|!=|>=|<=|>|<)\s*(?:'([^']*)'|\"([^\"]*)\"|([\w.:-]+))", clause.strip())
                    if not match:
                        raise ValueError("Use field == 'value' and bytes > 1000, or plain text. Fields: srcIp, dstIp, srcPort, dstPort, protocol, appProtocol, bytes, packets, duration, riskScore, attackType.")
                    field, op, quoted, double, bare = match.groups()
                    value = quoted if quoted is not None else double if double is not None else bare
                    numeric = field in ("srcPort", "dstPort", "bytes", "packets", "duration", "riskScore")
                    if numeric:
                        try:
                            value = float(value)
                        except ValueError as exc:
                            raise ValueError(f"{field} requires a number") from exc
                    elif op not in ("==", "!="):
                        raise ValueError("Text fields support only == and !=")
                    def matches(record):
                        actual = record.get(field, "")
                        expected = value
                        if not numeric:
                            actual, expected = str(actual).casefold(), str(expected).casefold()
                        return {"==": lambda: actual == expected, "!=": lambda: actual != expected, ">": lambda: actual > expected, "<": lambda: actual < expected, ">=": lambda: actual >= expected, "<=": lambda: actual <= expected}[op]()
                    records = [r for r in records if matches(r)]
            else:
                records = [r for r in records if query.casefold() in json.dumps(r).casefold()]
        return {"data": records[:1000], "total": len(records), "query": query, "facets": dict(Counter(f["appProtocol"] for f in records))}

    def replay(self):
        events = [{"timestamp": a["timestamp"], "type": "alert", "title": a["signature"], "entityId": a["id"], "source": "synthetic-demo" if a["synthetic"] else "ingested", "srcIp": a["srcIp"], "dstIp": a["dstIp"], "severity": a["severity"]} for a in self.all("alerts")]
        events.sort(key=lambda e: e["timestamp"])
        return {"events": events, "total": len(events), "mode": "recorded-alert-timeline"}

    def seed(self):
        base = datetime.now(timezone.utc) - timedelta(minutes=12)
        flows = []
        for i in range(36):
            flows.append({"srcIp": f"10.42.0.{10+i%5}", "dstIp": "10.42.0.20" if i%2 else "1.1.1.1", "srcPort": 40000+i, "dstPort": 443 if i%2 else 53, "protocol": "TCP" if i%2 else "UDP", "packets": 30+i, "bytes": 12000+i*500, "duration": 3+i/10, "timestamp": (base+timedelta(seconds=i*10)).isoformat(), "source": "demo-seed"})
        for i, port in enumerate((21,22,23,25,53,80,135,139,389,443)):
            flows.append({"srcIp": "10.42.0.10", "dstIp": "10.42.0.20", "srcPort": 50000+i, "dstPort": port, "protocol": "TCP", "packets": 3, "bytes": 180, "duration": .2, "timestamp": (base+timedelta(seconds=400+i*5)).isoformat(), "source": "demo-seed"})
        for offset, dst, port, size in ((480,"10.42.0.21",445,95000), (540,"8.8.8.8",443,8_000_000)):
            flows.append({"srcIp": "10.42.0.10", "dstIp": dst, "srcPort": 52000, "dstPort": port, "protocol": "TCP", "packets": 200, "bytes": size, "duration": 10, "timestamp": (base+timedelta(seconds=offset)).isoformat(), "source": "demo-seed"})
        self.ingest(flows)
        with self.lock, self.db:
            names = {"10.42.0.10": ("analyst-workstation", "workstation"), "10.42.0.20": ("web-server", "server"), "10.42.0.21": ("file-server", "server")}
            for host in self.all("hosts"):
                if host["ip"] in names:
                    host["hostname"], host["deviceType"] = names[host["ip"]]
                    host["evidence"] = "Explicit synthetic scenario label"
                    self.put("hosts", host)
            self.put("metadata", {"id": "seed", "createdAt": now(), "synthetic": True})
