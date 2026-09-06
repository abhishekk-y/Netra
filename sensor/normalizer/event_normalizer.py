"""Normalize Zeek and Suricata records while retaining their original payload."""
import base64
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import ipaddress
import struct
from typing import Any, Dict, Optional
import uuid


@dataclass
class NormalizedEvent:
    event_id: str
    sensor_id: str
    timestamp: datetime
    event_type: str
    source_ip: Optional[str]
    dest_ip: Optional[str]
    source_port: Optional[int]
    dest_port: Optional[int]
    protocol: Optional[str]
    community_id: Optional[str]
    payload: Dict[str, Any]


class EventNormalizer:
    def __init__(self, sensor_id: str):
        self.sensor_id = sensor_id

    @staticmethod
    def calculate_community_id(src_ip, dst_ip, src_port, dst_port, proto):
        """Community ID v1, seed 0, TCP/UDP/SCTP over IPv4/IPv6.

        Unsupported protocols return an empty ID; ICMP needs type/code mapping.
        Specification: https://github.com/corelight/community-id-spec
        """
        try:
            protocol = {"tcp": 6, "udp": 17, "sctp": 132}.get(str(proto).lower())
            if protocol is None:
                return ""
            src, dst = ipaddress.ip_address(src_ip), ipaddress.ip_address(dst_ip)
            if src.version != dst.version:
                return ""
            sport, dport = int(src_port), int(dst_port)
            if (src.packed, sport) > (dst.packed, dport):
                src, dst, sport, dport = dst, src, dport, sport
            data = struct.pack("!H", 0) + src.packed + dst.packed
            data += struct.pack("!BBHH", protocol, 0, sport, dport)
            return "1:" + base64.b64encode(hashlib.sha1(data).digest()).decode("ascii")
        except (ValueError, TypeError, struct.error):
            return ""

    @staticmethod
    def _port(value):
        if value in (None, "", "-"):
            return None
        port = int(value)
        if not 0 <= port <= 65535:
            raise ValueError("Port outside 0..65535")
        return port

    @staticmethod
    def _timestamp(value):
        if value in (None, "", "-"):
            return datetime.now(timezone.utc)
        if isinstance(value, (int, float)) or str(value).replace(".", "", 1).isdigit():
            return datetime.fromtimestamp(float(value), timezone.utc)
        timestamp = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return timestamp.replace(tzinfo=timezone.utc) if timestamp.tzinfo is None else timestamp

    def _normalize(self, raw_event, source):
        try:
            zeek = source == "zeek"
            src = raw_event.get("id.orig_h" if zeek else "src_ip")
            dst = raw_event.get("id.resp_h" if zeek else "dest_ip")
            for address in (src, dst):
                if address is not None:
                    ipaddress.ip_address(address)
            sport = self._port(raw_event.get("id.orig_p" if zeek else "src_port"))
            dport = self._port(raw_event.get("id.resp_p" if zeek else "dest_port"))
            protocol = str(raw_event.get("proto", "")).lower()
            community_id = raw_event.get("community_id")
            if not community_id and src and dst and sport is not None and dport is not None:
                community_id = self.calculate_community_id(src, dst, sport, dport, protocol) or None
            return NormalizedEvent(
                event_id=str(uuid.uuid4()), sensor_id=self.sensor_id,
                timestamp=self._timestamp(raw_event.get("ts" if zeek else "timestamp")),
                event_type=source + "_" + str(raw_event.get("log_type" if zeek else "event_type", "unknown")),
                source_ip=src, dest_ip=dst, source_port=sport, dest_port=dport,
                protocol=protocol, community_id=community_id, payload=dict(raw_event))
        except (ValueError, TypeError, OverflowError):
            return None

    def normalize_suricata(self, raw_event):
        return self._normalize(raw_event, "suricata")

    def normalize_zeek(self, raw_event):
        return self._normalize(raw_event, "zeek")
