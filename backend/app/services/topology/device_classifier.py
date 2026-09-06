from typing import Tuple, List, Dict, Any

class DeviceClassifier:
    def classify(self, host_data: Dict[str, Any]) -> Tuple[str, float, List[str]]:
        evidence_list = []
        scores = {
            "Router": 0.0,
            "Switch": 0.0,
            "Firewall": 0.0,
            "Server": 0.0,
            "Workstation": 0.0,
            "IoT": 0.0,
            "Unknown": 0.1
        }
        
        # Check explicit device types identified by discovery
        dt_list = host_data.get("device_type", [])
        if "Switch" in dt_list:
            scores["Switch"] += 0.8
            evidence_list.append("Observed Switch protocols (LLDP/STP)")
            
        # Check vendor info
        vendors = host_data.get("vendor", [])
        if any("Cisco" in v for v in vendors):
            scores["Router"] += 0.3
            scores["Switch"] += 0.3
            evidence_list.append("Cisco MAC OUI")
        if any("Raspberry" in v for v in vendors):
            scores["IoT"] += 0.6
            evidence_list.append("Raspberry Pi MAC OUI")
            
        # Check DHCP
        dhcp_vendors = host_data.get("dhcp_vendor", [])
        if any("MSFT" in v for v in dhcp_vendors):
            scores["Workstation"] += 0.5
            scores["Server"] += 0.2
            evidence_list.append("Windows DHCP Vendor Class")
            
        # Check open ports/services (if provided in host_data)
        ports = host_data.get("open_ports", [])
        if 80 in ports or 443 in ports or 22 in ports:
            scores["Server"] += 0.4
            evidence_list.append("Hosting well-known server ports")
            
        best_match = max(scores.items(), key=lambda x: x[1])
        device_type = best_match[0]
        confidence = min(best_match[1], 1.0)
        
        if confidence < 0.2:
            device_type = "Unknown"
            
        return device_type, confidence, evidence_list
