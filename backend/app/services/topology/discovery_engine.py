from typing import Dict, Any, List
from app.models.event import NormalizedEvent

OUI_MAPPING = {
    "00:50:56": "VMware",
    "00:0C:29": "VMware",
    "00:15:5D": "Microsoft",
    "00:00:5E": "IANA (VRRP)",
    "00:1A:11": "Google",
    "DC:A6:32": "Raspberry Pi",
    "00:14:22": "Dell",
    "00:25:90": "Super Micro",
    "00:1E:67": "Intel",
    "E4:8D:8C": "Routerboard",
    "00:01:42": "Cisco",
    "00:02:B9": "Cisco",
}

class TopologyDiscoveryEngine:
    def __init__(self):
        self.hosts_evidence: Dict[str, Dict[str, Any]] = {}
        self.subnet_cache: List[str] = []
        
    def process_event(self, event: NormalizedEvent) -> None:
        ev_type = event.event_type.lower()
        if ev_type == "arp":
            self._handle_arp(event)
        elif ev_type == "dhcp":
            self._handle_dhcp(event)
        elif ev_type == "dns":
            self._handle_dns(event)
        elif ev_type == "lldp":
            self._handle_lldp(event)
        elif ev_type == "stp":
            self._handle_stp(event)
        elif ev_type in ["flow", "connection"]:
            self._handle_flow(event)
            
    def _handle_arp(self, event: NormalizedEvent) -> None:
        mac = event.data.get("mac")
        ip = event.data.get("ip")
        if mac and ip:
            self._add_evidence(ip, "mac", mac)
            self._add_evidence(ip, "vendor", self._resolve_oui(mac))

    def _handle_dhcp(self, event: NormalizedEvent) -> None:
        ip = event.data.get("assigned_ip")
        hostname = event.data.get("hostname")
        vendor_class = event.data.get("vendor_class")
        if ip:
            if hostname:
                self._add_evidence(ip, "hostname", hostname)
            if vendor_class:
                self._add_evidence(ip, "dhcp_vendor", vendor_class)
                
    def _handle_dns(self, event: NormalizedEvent) -> None:
        # A record resolution mapping
        query = event.data.get("query")
        answers = event.data.get("answers", [])
        for ans in answers:
            self._add_evidence(ans, "dns_name", query)
            
    def _handle_lldp(self, event: NormalizedEvent) -> None:
        ip = event.source_ip
        sys_name = event.data.get("system_name")
        if ip and sys_name:
            self._add_evidence(ip, "lldp_name", sys_name)
            self._add_evidence(ip, "device_type", "Switch")
            
    def _handle_stp(self, event: NormalizedEvent) -> None:
        ip = event.source_ip
        if ip:
            self._add_evidence(ip, "protocol", "STP")
            self._add_evidence(ip, "device_type", "Switch")
            
    def _handle_flow(self, event: NormalizedEvent) -> None:
        sip = event.source_ip
        dip = event.destination_ip
        if sip and dip:
            self._detect_gateway(sip, dip)
            self._detect_subnet([sip, dip])
            
    def _resolve_oui(self, mac: str) -> str:
        prefix = mac.upper()[:8].replace("-", ":")
        return OUI_MAPPING.get(prefix, "Unknown")
        
    def _detect_gateway(self, src_ip: str, dst_ip: str) -> None:
        # Simplistic heuristic: if communicating with public IP, src gateway is likely involved
        # In a real implementation, this tracks MAC address routing transitions.
        pass
        
    def _detect_subnet(self, ip_list: List[str]) -> None:
        # Basic /24 inference for local IPs
        for ip in ip_list:
            if ip.startswith("10.") or ip.startswith("192.168.") or ip.startswith("172."):
                parts = ip.split(".")
                if len(parts) == 4:
                    subnet = f"{parts[0]}.{parts[1]}.{parts[2]}.0/24"
                    if subnet not in self.subnet_cache:
                        self.subnet_cache.append(subnet)
                        
    def _add_evidence(self, ip: str, key: str, value: Any) -> None:
        if ip not in self.hosts_evidence:
            self.hosts_evidence[ip] = {}
        if key not in self.hosts_evidence[ip]:
            self.hosts_evidence[ip][key] = []
        if value not in self.hosts_evidence[ip][key]:
            self.hosts_evidence[ip][key].append(value)
