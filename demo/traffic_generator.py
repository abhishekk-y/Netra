"""Synthetic flow records for repeatable demonstrations. No network probes are sent."""
from datetime import datetime, timezone
import json
from urllib.request import Request, urlopen


class TrafficGenerator:
    PHASES = ("normal", "recon", "credential", "lateral", "c2", "exfiltration")

    def __init__(self, target_host="127.0.0.1", api_url=None):
        self.api_url = (api_url or f"http://{target_host}:8000").rstrip("/")

    def generate(self, phase="normal"):
        if phase not in self.PHASES:
            raise ValueError(f"Unknown phase: {phase}")
        now = datetime.now(timezone.utc).isoformat()
        base = dict(srcIp="10.0.0.10", dstIp="10.0.0.20", srcPort=51000,
                    dstPort=443, protocol="TCP", packets=12, bytes=4800,
                    duration=2.0, timestamp=now, source="demo-replay")
        if phase == "normal":
            return [dict(base, srcIp=f"10.0.0.{10+i}", srcPort=51000+i) for i in range(4)]
        if phase == "recon":
            return [dict(base, dstPort=p, packets=2, bytes=120, duration=0.5)
                    for p in (21, 22, 23, 25, 53, 80, 110, 135, 139, 443, 445, 3389)]
        if phase == "credential":
            return [dict(base, dstPort=22, srcPort=52000+i, packets=8, bytes=600)
                    for i in range(12)]
        if phase == "lateral":
            return [dict(base, dstIp=f"10.0.0.{30+i}", dstPort=445,
                         packets=40, bytes=24000) for i in range(3)]
        if phase == "c2":
            return [dict(base, dstIp="198.51.100.20", packets=4, bytes=240,
                         duration=5.0, srcPort=53000+i) for i in range(4)]
        return [dict(base, dstIp="8.8.8.8", packets=12000,
                     bytes=8*1024*1024, duration=30.0)]

    def submit(self, phase="normal"):
        request = Request(self.api_url + "/api/ingest/flows",
                          data=json.dumps({"flows": self.generate(phase)}).encode(),
                          headers={"Content-Type": "application/json"}, method="POST")
        with urlopen(request, timeout=15) as response:
            return json.load(response)
