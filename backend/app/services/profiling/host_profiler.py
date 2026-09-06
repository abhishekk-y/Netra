"""
Netra Host Profiler Service
Builds and maintains comprehensive profiles for every discovered host.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Optional
from collections import defaultdict
import statistics


class HostProfile:
    """Complete profile for a single network host."""

    __slots__ = (
        "host_id", "ip_addresses", "mac_addresses", "hostname",
        "vendor", "os_estimate", "os_confidence", "device_type",
        "device_type_confidence", "device_type_evidence",
        "first_seen", "last_seen", "vlan_id", "subnet", "gateway_ip",
        "observed_ports", "observed_protocols", "observed_services",
        "tls_fingerprints", "total_packets", "total_bytes",
        "total_flows", "top_peers", "top_protocols",
        "bandwidth_history", "risk_score", "anomaly_score",
        "alerts", "attack_techniques", "incidents",
        "normal_peers", "normal_ports", "normal_hours",
        "normal_bandwidth", "normal_protocols",
        "_peer_counter", "_protocol_counter", "_port_counter",
        "_hourly_activity", "_bandwidth_samples",
    )

    def __init__(self, host_id: str, ip: str):
        self.host_id = host_id
        self.ip_addresses: list[str] = [ip]
        self.mac_addresses: list[str] = []
        self.hostname: Optional[str] = None
        self.vendor: Optional[str] = None
        self.os_estimate: Optional[str] = None
        self.os_confidence: float = 0.0
        self.device_type: str = "unknown"
        self.device_type_confidence: float = 0.0
        self.device_type_evidence: list[str] = []
        self.first_seen: datetime = datetime.now(timezone.utc)
        self.last_seen: datetime = datetime.now(timezone.utc)
        self.vlan_id: Optional[int] = None
        self.subnet: Optional[str] = None
        self.gateway_ip: Optional[str] = None
        self.observed_ports: set[int] = set()
        self.observed_protocols: set[str] = set()
        self.observed_services: dict[int, str] = {}
        self.tls_fingerprints: set[str] = set()
        self.total_packets: int = 0
        self.total_bytes: int = 0
        self.total_flows: int = 0
        self.top_peers: dict[str, int] = {}
        self.top_protocols: dict[str, int] = {}
        self.bandwidth_history: list[tuple[datetime, float]] = []
        self.risk_score: float = 0.0
        self.anomaly_score: float = 0.0
        self.alerts: list[dict] = []
        self.attack_techniques: list[dict] = []
        self.incidents: list[str] = []
        self.normal_peers: set[str] = set()
        self.normal_ports: set[int] = set()
        self.normal_hours: set[int] = set()
        self.normal_bandwidth: float = 0.0
        self.normal_protocols: set[str] = set()
        self._peer_counter: dict[str, int] = defaultdict(int)
        self._protocol_counter: dict[str, int] = defaultdict(int)
        self._port_counter: dict[str, int] = defaultdict(int)
        self._hourly_activity: dict[int, int] = defaultdict(int)
        self._bandwidth_samples: list[float] = []

    def to_dict(self) -> dict[str, Any]:
        return {
            "host_id": self.host_id,
            "ip_addresses": self.ip_addresses,
            "mac_addresses": self.mac_addresses,
            "hostname": self.hostname,
            "vendor": self.vendor,
            "os_estimate": self.os_estimate,
            "os_confidence": self.os_confidence,
            "device_type": self.device_type,
            "device_type_confidence": self.device_type_confidence,
            "device_type_evidence": self.device_type_evidence,
            "first_seen": self.first_seen.isoformat(),
            "last_seen": self.last_seen.isoformat(),
            "vlan_id": self.vlan_id,
            "subnet": self.subnet,
            "gateway_ip": self.gateway_ip,
            "observed_ports": sorted(self.observed_ports),
            "observed_protocols": sorted(self.observed_protocols),
            "observed_services": self.observed_services,
            "tls_fingerprints": sorted(self.tls_fingerprints),
            "total_packets": self.total_packets,
            "total_bytes": self.total_bytes,
            "total_flows": self.total_flows,
            "top_peers": dict(sorted(self._peer_counter.items(), key=lambda x: -x[1])[:20]),
            "top_protocols": dict(sorted(self._protocol_counter.items(), key=lambda x: -x[1])[:10]),
            "bandwidth_history": [(ts.isoformat(), bw) for ts, bw in self.bandwidth_history[-100:]],
            "risk_score": self.risk_score,
            "anomaly_score": self.anomaly_score,
            "alerts_count": len(self.alerts),
            "attack_techniques": self.attack_techniques,
            "incidents": self.incidents,
            "behavior": {
                "normal_peers": sorted(self.normal_peers),
                "normal_ports": sorted(self.normal_ports),
                "normal_hours": sorted(self.normal_hours),
                "normal_bandwidth": self.normal_bandwidth,
                "normal_protocols": sorted(self.normal_protocols),
            },
        }


SERVICE_PORT_MAP: dict[int, str] = {
    21: "ftp", 22: "ssh", 23: "telnet", 25: "smtp", 53: "dns",
    67: "dhcp-server", 68: "dhcp-client", 80: "http", 110: "pop3",
    123: "ntp", 143: "imap", 161: "snmp", 443: "https", 445: "smb",
    993: "imaps", 995: "pop3s", 1433: "mssql", 1521: "oracle",
    3306: "mysql", 3389: "rdp", 5432: "postgresql", 5900: "vnc",
    6379: "redis", 8080: "http-alt", 8443: "https-alt", 9200: "elasticsearch",
    27017: "mongodb",
}


class HostProfiler:
    """Builds and maintains comprehensive profiles for discovered hosts."""

    def __init__(self):
        self._profiles: dict[str, HostProfile] = {}
        self._ip_to_host: dict[str, str] = {}

    def get_or_create_profile(self, ip: str) -> HostProfile:
        if ip in self._ip_to_host:
            return self._profiles[self._ip_to_host[ip]]
        host_id = str(uuid.uuid4())
        profile = HostProfile(host_id, ip)
        self._profiles[host_id] = profile
        self._ip_to_host[ip] = host_id
        return profile

    def get_profile_by_ip(self, ip: str) -> Optional[HostProfile]:
        host_id = self._ip_to_host.get(ip)
        if host_id:
            return self._profiles.get(host_id)
        return None

    def get_profile(self, host_id: str) -> Optional[HostProfile]:
        return self._profiles.get(host_id)

    def get_all_profiles(self) -> list[HostProfile]:
        return list(self._profiles.values())

    def process_flow_event(self, event: dict[str, Any]) -> None:
        src_ip = event.get("source_ip", event.get("src_ip", ""))
        dst_ip = event.get("destination_ip", event.get("dst_ip", ""))
        src_port = event.get("source_port", event.get("src_port"))
        dst_port = event.get("destination_port", event.get("dst_port"))
        protocol = event.get("protocol", "unknown")
        timestamp = event.get("timestamp", datetime.now(timezone.utc))
        packets = event.get("packets_forward", 0) + event.get("packets_backward", 0)
        total_bytes = event.get("bytes_forward", 0) + event.get("bytes_backward", 0)

        if isinstance(timestamp, str):
            try:
                timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            except (ValueError, TypeError):
                timestamp = datetime.now(timezone.utc)

        if src_ip:
            src_profile = self.get_or_create_profile(src_ip)
            self._update_profile_from_flow(
                src_profile, dst_ip, src_port, dst_port, protocol,
                timestamp, packets, total_bytes, direction="outbound"
            )

        if dst_ip:
            dst_profile = self.get_or_create_profile(dst_ip)
            self._update_profile_from_flow(
                dst_profile, src_ip, dst_port, src_port, protocol,
                timestamp, packets, total_bytes, direction="inbound"
            )

    def _update_profile_from_flow(
        self, profile: HostProfile, peer_ip: str,
        local_port: Optional[int], remote_port: Optional[int],
        protocol: str, timestamp: datetime,
        packets: int, total_bytes: int, direction: str
    ) -> None:
        profile.last_seen = max(profile.last_seen, timestamp)
        profile.total_packets += packets
        profile.total_bytes += total_bytes
        profile.total_flows += 1

        if peer_ip:
            profile._peer_counter[peer_ip] += 1

        if protocol:
            proto_upper = protocol.upper()
            profile.observed_protocols.add(proto_upper)
            profile._protocol_counter[proto_upper] += 1

        if local_port is not None and local_port > 0:
            profile.observed_ports.add(local_port)
            profile._port_counter[local_port] += 1
            if local_port in SERVICE_PORT_MAP:
                profile.observed_services[local_port] = SERVICE_PORT_MAP[local_port]

        if remote_port is not None and remote_port > 0:
            if remote_port in SERVICE_PORT_MAP:
                profile.observed_services[remote_port] = SERVICE_PORT_MAP[remote_port]

        hour = timestamp.hour
        profile._hourly_activity[hour] += 1

        duration_ms = max(1, packets * 10)
        bw = (total_bytes * 8) / (duration_ms / 1000) if duration_ms > 0 else 0
        profile._bandwidth_samples.append(bw)
        if len(profile._bandwidth_samples) > 1000:
            profile._bandwidth_samples = profile._bandwidth_samples[-500:]
        profile.bandwidth_history.append((timestamp, bw))
        if len(profile.bandwidth_history) > 200:
            profile.bandwidth_history = profile.bandwidth_history[-100:]

    def process_dns_event(self, event: dict[str, Any]) -> None:
        src_ip = event.get("source_ip", event.get("src_ip", ""))
        query = event.get("query", "")
        if src_ip and query:
            profile = self.get_or_create_profile(src_ip)
            profile.observed_protocols.add("DNS")

    def process_tls_event(self, event: dict[str, Any]) -> None:
        src_ip = event.get("source_ip", event.get("src_ip", ""))
        ja4 = event.get("ja4", "")
        if src_ip:
            profile = self.get_or_create_profile(src_ip)
            profile.observed_protocols.add("TLS")
            if ja4:
                profile.tls_fingerprints.add(ja4)

    def update_host_identity(self, ip: str, **kwargs: Any) -> None:
        profile = self.get_or_create_profile(ip)
        if "hostname" in kwargs and kwargs["hostname"]:
            profile.hostname = kwargs["hostname"]
        if "mac" in kwargs and kwargs["mac"]:
            mac = kwargs["mac"].lower()
            if mac not in profile.mac_addresses:
                profile.mac_addresses.append(mac)
        if "vendor" in kwargs and kwargs["vendor"]:
            profile.vendor = kwargs["vendor"]
        if "os_estimate" in kwargs:
            profile.os_estimate = kwargs["os_estimate"]
            profile.os_confidence = kwargs.get("os_confidence", 0.5)
        if "device_type" in kwargs:
            profile.device_type = kwargs["device_type"]
            profile.device_type_confidence = kwargs.get("device_type_confidence", 0.5)
            profile.device_type_evidence = kwargs.get("device_type_evidence", [])
        if "vlan_id" in kwargs:
            profile.vlan_id = kwargs["vlan_id"]
        if "subnet" in kwargs:
            profile.subnet = kwargs["subnet"]
        if "gateway_ip" in kwargs:
            profile.gateway_ip = kwargs["gateway_ip"]

    def update_risk(self, ip: str, risk_score: float, anomaly_score: float = 0.0) -> None:
        profile = self.get_profile_by_ip(ip)
        if profile:
            profile.risk_score = risk_score
            profile.anomaly_score = anomaly_score

    def add_alert(self, ip: str, alert: dict[str, Any]) -> None:
        profile = self.get_profile_by_ip(ip)
        if profile:
            profile.alerts.append(alert)
            if len(profile.alerts) > 500:
                profile.alerts = profile.alerts[-250:]

    def add_technique(self, ip: str, technique: dict[str, Any]) -> None:
        profile = self.get_profile_by_ip(ip)
        if profile:
            existing_ids = {t.get("technique_id") for t in profile.attack_techniques}
            if technique.get("technique_id") not in existing_ids:
                profile.attack_techniques.append(technique)

    def compute_behavior_summary(self, ip: str) -> dict[str, Any]:
        profile = self.get_profile_by_ip(ip)
        if not profile:
            return {}
        top_peers = sorted(profile._peer_counter.items(), key=lambda x: -x[1])[:10]
        top_ports = sorted(profile._port_counter.items(), key=lambda x: -x[1])[:10]
        active_hours = sorted(profile._hourly_activity.items(), key=lambda x: -x[1])[:6]
        avg_bw = statistics.mean(profile._bandwidth_samples) if profile._bandwidth_samples else 0
        return {
            "host_id": profile.host_id,
            "ip": ip,
            "top_peers": [{"ip": p, "count": c} for p, c in top_peers],
            "top_ports": [{"port": p, "count": c} for p, c in top_ports],
            "active_hours": [{"hour": h, "count": c} for h, c in active_hours],
            "protocol_distribution": dict(profile._protocol_counter),
            "average_bandwidth_bps": round(avg_bw, 2),
            "total_flows": profile.total_flows,
            "total_bytes": profile.total_bytes,
            "unique_peers": len(profile._peer_counter),
            "unique_ports": len(profile.observed_ports),
        }

    def get_stats(self) -> dict[str, int]:
        return {
            "total_profiles": len(self._profiles),
            "total_ips_tracked": len(self._ip_to_host),
        }
