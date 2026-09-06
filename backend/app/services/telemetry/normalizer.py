from datetime import datetime, timezone
import uuid
from typing import Dict, Any

from app.models.event import NormalizedEvent
from app.services.telemetry.community_id import calc_community_id

class EventNormalizer:
    
    def _create_base_event(self, record: dict, source: str, event_type: str) -> NormalizedEvent:
        return NormalizedEvent(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc), # Ideally parse from record['ts']
            sensor_id=record.get("sensor_id", "unknown"),
            event_type=event_type,
            raw_source=source,
            severity=1,
            data=record,
            confidence=1.0
        )

    def _get_protocol_num(self, proto_str: str) -> int:
        mapping = {"tcp": 6, "udp": 17, "icmp": 1, "sctp": 132}
        return mapping.get(proto_str.lower(), 6)

    def normalize_zeek_conn(self, record: dict) -> NormalizedEvent:
        event = self._create_base_event(record, "zeek", "connection")
        event.source_ip = record.get("id.orig_h")
        event.source_port = record.get("id.orig_p")
        event.destination_ip = record.get("id.resp_h")
        event.destination_port = record.get("id.resp_p")
        event.protocol = record.get("proto")
        event.session_id = record.get("uid")
        
        if event.source_ip and event.destination_ip:
            event.community_id = calc_community_id(
                event.source_ip, event.destination_ip,
                event.source_port or 0, event.destination_port or 0,
                self._get_protocol_num(str(event.protocol))
            )
        return event

    def normalize_zeek_dns(self, record: dict) -> NormalizedEvent:
        event = self._create_base_event(record, "zeek", "dns")
        event.source_ip = record.get("id.orig_h")
        event.source_port = record.get("id.orig_p")
        event.destination_ip = record.get("id.resp_h")
        event.destination_port = record.get("id.resp_p")
        event.protocol = record.get("proto")
        event.session_id = record.get("uid")
        
        if event.source_ip and event.destination_ip:
            event.community_id = calc_community_id(
                event.source_ip, event.destination_ip,
                event.source_port or 0, event.destination_port or 0,
                self._get_protocol_num(str(event.protocol))
            )
        return event

    def normalize_zeek_http(self, record: dict) -> NormalizedEvent:
        event = self._create_base_event(record, "zeek", "http")
        event.source_ip = record.get("id.orig_h")
        event.source_port = record.get("id.orig_p")
        event.destination_ip = record.get("id.resp_h")
        event.destination_port = record.get("id.resp_p")
        event.protocol = "tcp"
        event.session_id = record.get("uid")
        
        if event.source_ip and event.destination_ip:
            event.community_id = calc_community_id(
                event.source_ip, event.destination_ip,
                event.source_port or 0, event.destination_port or 0,
                6
            )
        return event

    def normalize_zeek_ssl(self, record: dict) -> NormalizedEvent:
        event = self._create_base_event(record, "zeek", "ssl")
        event.source_ip = record.get("id.orig_h")
        event.source_port = record.get("id.orig_p")
        event.destination_ip = record.get("id.resp_h")
        event.destination_port = record.get("id.resp_p")
        event.protocol = "tcp"
        event.session_id = record.get("uid")
        
        if event.source_ip and event.destination_ip:
            event.community_id = calc_community_id(
                event.source_ip, event.destination_ip,
                event.source_port or 0, event.destination_port or 0,
                6
            )
        return event

    def normalize_suricata_alert(self, record: dict) -> NormalizedEvent:
        event = self._create_base_event(record, "suricata", "alert")
        event.source_ip = record.get("src_ip")
        event.source_port = record.get("src_port")
        event.destination_ip = record.get("dest_ip")
        event.destination_port = record.get("dest_port")
        event.protocol = record.get("proto")
        event.severity = record.get("alert", {}).get("severity", 1)
        
        if event.source_ip and event.destination_ip:
            event.community_id = calc_community_id(
                event.source_ip, event.destination_ip,
                event.source_port or 0, event.destination_port or 0,
                self._get_protocol_num(str(event.protocol))
            )
        return event

    def normalize_suricata_flow(self, record: dict) -> NormalizedEvent:
        event = self._create_base_event(record, "suricata", "flow")
        event.source_ip = record.get("src_ip")
        event.source_port = record.get("src_port")
        event.destination_ip = record.get("dest_ip")
        event.destination_port = record.get("dest_port")
        event.protocol = record.get("proto")
        
        if event.source_ip and event.destination_ip:
            event.community_id = calc_community_id(
                event.source_ip, event.destination_ip,
                event.source_port or 0, event.destination_port or 0,
                self._get_protocol_num(str(event.protocol))
            )
        return event

    def normalize_pcap_packet(self, packet_data: dict) -> NormalizedEvent:
        event = self._create_base_event(packet_data, "pcap", "packet")
        event.source_ip = packet_data.get("src_ip")
        event.source_port = packet_data.get("src_port")
        event.destination_ip = packet_data.get("dst_ip")
        event.destination_port = packet_data.get("dst_port")
        event.protocol = packet_data.get("protocol")
        
        if event.source_ip and event.destination_ip:
            event.community_id = calc_community_id(
                event.source_ip, event.destination_ip,
                event.source_port or 0, event.destination_port or 0,
                self._get_protocol_num(str(event.protocol))
            )
        return event
