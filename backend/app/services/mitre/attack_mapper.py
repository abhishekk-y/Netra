"""
Netra — MITRE ATT&CK Technique Database
Network-observable ATT&CK techniques with detection mapping.
"""
from __future__ import annotations

from typing import Any


MITRE_TACTICS: list[dict[str, str]] = [
    {"id": "TA0043", "name": "Reconnaissance", "short": "recon"},
    {"id": "TA0042", "name": "Resource Development", "short": "resource_dev"},
    {"id": "TA0001", "name": "Initial Access", "short": "initial_access"},
    {"id": "TA0002", "name": "Execution", "short": "execution"},
    {"id": "TA0003", "name": "Persistence", "short": "persistence"},
    {"id": "TA0004", "name": "Privilege Escalation", "short": "priv_esc"},
    {"id": "TA0005", "name": "Defense Evasion", "short": "def_evasion"},
    {"id": "TA0006", "name": "Credential Access", "short": "cred_access"},
    {"id": "TA0007", "name": "Discovery", "short": "discovery"},
    {"id": "TA0008", "name": "Lateral Movement", "short": "lateral"},
    {"id": "TA0009", "name": "Collection", "short": "collection"},
    {"id": "TA0011", "name": "Command and Control", "short": "c2"},
    {"id": "TA0010", "name": "Exfiltration", "short": "exfil"},
    {"id": "TA0040", "name": "Impact", "short": "impact"},
]

MITRE_TECHNIQUES: list[dict[str, Any]] = [
    # Reconnaissance
    {"id": "T1595", "name": "Active Scanning", "tactic": "TA0043",
     "detection": "Port scan detection, SYN flood patterns, sequential port access",
     "network_observable": True},
    {"id": "T1595.001", "name": "Scanning IP Blocks", "tactic": "TA0043",
     "detection": "Sequential IP access, ICMP sweep patterns",
     "network_observable": True},
    {"id": "T1595.002", "name": "Vulnerability Scanning", "tactic": "TA0043",
     "detection": "Known scanner signatures, service probing patterns",
     "network_observable": True},
    {"id": "T1046", "name": "Network Service Discovery", "tactic": "TA0043",
     "detection": "Multiple port connections to single host, service banner grabbing",
     "network_observable": True},
    {"id": "T1018", "name": "Remote System Discovery", "tactic": "TA0007",
     "detection": "ARP sweep, NetBIOS enumeration, DNS zone transfer attempts",
     "network_observable": True},

    # Initial Access
    {"id": "T1190", "name": "Exploit Public-Facing Application", "tactic": "TA0001",
     "detection": "Web attack signatures, SQL injection patterns, abnormal HTTP payloads",
     "network_observable": True},
    {"id": "T1133", "name": "External Remote Services", "tactic": "TA0001",
     "detection": "RDP/SSH/VPN connections from unusual sources",
     "network_observable": True},
    {"id": "T1078", "name": "Valid Accounts", "tactic": "TA0001",
     "detection": "Authentication from new source IPs, off-hours access",
     "network_observable": True},

    # Credential Access
    {"id": "T1110", "name": "Brute Force", "tactic": "TA0006",
     "detection": "Repeated authentication failures, rapid login attempts",
     "network_observable": True},
    {"id": "T1110.001", "name": "Password Guessing", "tactic": "TA0006",
     "detection": "Multiple failed SSH/FTP/HTTP auth attempts",
     "network_observable": True},
    {"id": "T1110.003", "name": "Password Spraying", "tactic": "TA0006",
     "detection": "Single password across many accounts, distributed auth failures",
     "network_observable": True},
    {"id": "T1557", "name": "Adversary-in-the-Middle", "tactic": "TA0006",
     "detection": "ARP spoofing, LLMNR/NBT-NS poisoning, abnormal ARP patterns",
     "network_observable": True},

    # Lateral Movement
    {"id": "T1021", "name": "Remote Services", "tactic": "TA0008",
     "detection": "Unusual SSH/RDP/SMB connections between internal hosts",
     "network_observable": True},
    {"id": "T1021.001", "name": "Remote Desktop Protocol", "tactic": "TA0008",
     "detection": "RDP connections (port 3389) to new internal destinations",
     "network_observable": True},
    {"id": "T1021.002", "name": "SMB/Windows Admin Shares", "tactic": "TA0008",
     "detection": "SMB connections (port 445) to new internal destinations",
     "network_observable": True},
    {"id": "T1021.004", "name": "SSH", "tactic": "TA0008",
     "detection": "SSH connections to new internal hosts from compromised systems",
     "network_observable": True},
    {"id": "T1570", "name": "Lateral Tool Transfer", "tactic": "TA0008",
     "detection": "Large file transfers between internal hosts via SMB/SSH",
     "network_observable": True},

    # Command and Control
    {"id": "T1071", "name": "Application Layer Protocol", "tactic": "TA0011",
     "detection": "Unusual HTTP/HTTPS/DNS patterns, abnormal User-Agent strings",
     "network_observable": True},
    {"id": "T1071.001", "name": "Web Protocols", "tactic": "TA0011",
     "detection": "HTTP beaconing, unusual HTTP methods, encoded payloads",
     "network_observable": True},
    {"id": "T1071.004", "name": "DNS", "tactic": "TA0011",
     "detection": "DNS tunneling indicators, high-entropy domain names, TXT record abuse",
     "network_observable": True},
    {"id": "T1573", "name": "Encrypted Channel", "tactic": "TA0011",
     "detection": "Unusual TLS fingerprints, self-signed certificates, non-standard ports",
     "network_observable": True},
    {"id": "T1095", "name": "Non-Application Layer Protocol", "tactic": "TA0011",
     "detection": "ICMP tunneling, raw TCP/UDP to unusual ports",
     "network_observable": True},
    {"id": "T1571", "name": "Non-Standard Port", "tactic": "TA0011",
     "detection": "Common protocols on uncommon ports, HTTP on non-80/443",
     "network_observable": True},
    {"id": "T1572", "name": "Protocol Tunneling", "tactic": "TA0011",
     "detection": "DNS over HTTPS, SSH tunneling, protocol anomalies",
     "network_observable": True},
    {"id": "T1568", "name": "Dynamic Resolution", "tactic": "TA0011",
     "detection": "DGA domain patterns, flux DNS, fast-flux detection",
     "network_observable": True},

    # Exfiltration
    {"id": "T1041", "name": "Exfiltration Over C2 Channel", "tactic": "TA0010",
     "detection": "Large outbound data on C2 connections, unusual byte ratios",
     "network_observable": True},
    {"id": "T1048", "name": "Exfiltration Over Alternative Protocol", "tactic": "TA0010",
     "detection": "DNS exfiltration, ICMP exfiltration, unusual protocol data volumes",
     "network_observable": True},
    {"id": "T1048.003", "name": "Exfiltration Over Unencrypted Protocol", "tactic": "TA0010",
     "detection": "FTP/HTTP large uploads to external destinations",
     "network_observable": True},
    {"id": "T1567", "name": "Exfiltration Over Web Service", "tactic": "TA0010",
     "detection": "Large uploads to cloud storage, file sharing services",
     "network_observable": True},

    # Impact
    {"id": "T1498", "name": "Network Denial of Service", "tactic": "TA0040",
     "detection": "Traffic volume spikes, SYN floods, UDP floods",
     "network_observable": True},
    {"id": "T1499", "name": "Endpoint Denial of Service", "tactic": "TA0040",
     "detection": "Application-layer floods, slowloris patterns",
     "network_observable": True},

    # Discovery
    {"id": "T1049", "name": "System Network Connections Discovery", "tactic": "TA0007",
     "detection": "Netstat-like queries, connection enumeration patterns",
     "network_observable": True},
    {"id": "T1016", "name": "System Network Configuration Discovery", "tactic": "TA0007",
     "detection": "DHCP/DNS/ARP enumeration, route discovery",
     "network_observable": True},
]


class ATTACKMapper:
    """Maps detections to MITRE ATT&CK tactics and techniques."""

    def __init__(self):
        self._techniques = {t["id"]: t for t in MITRE_TECHNIQUES}
        self._tactics = {t["id"]: t for t in MITRE_TACTICS}
        self._observed: dict[str, dict] = {}
        self._forecast: dict[str, dict] = {}

    def map_detection(self, attack_type: str, confidence: float,
                      evidence: list[str]) -> list[dict[str, Any]]:
        mapping: dict[str, list[str]] = {
            "reconnaissance": ["T1595", "T1046"],
            "portscan": ["T1595", "T1595.001"],
            "scanning": ["T1595", "T1595.002"],
            "brute_force": ["T1110", "T1110.001"],
            "credential_access": ["T1110", "T1110.003"],
            "ssh_bruteforce": ["T1110.001", "T1021.004"],
            "web_attack": ["T1190"],
            "sql_injection": ["T1190"],
            "xss": ["T1190"],
            "initial_access": ["T1190", "T1133"],
            "lateral_movement": ["T1021", "T1570"],
            "botnet": ["T1071", "T1568"],
            "c2": ["T1071", "T1573"],
            "command_and_control": ["T1071", "T1571"],
            "dos": ["T1498", "T1499"],
            "ddos": ["T1498"],
            "exfiltration": ["T1041", "T1048"],
        }
        technique_ids = mapping.get(attack_type.lower(), [])
        results = []
        for tid in technique_ids:
            tech = self._techniques.get(tid)
            if tech:
                entry = {
                    "technique_id": tid,
                    "technique_name": tech["name"],
                    "tactic_id": tech["tactic"],
                    "tactic_name": self._tactics.get(tech["tactic"], {}).get("name", ""),
                    "confidence": round(confidence, 4),
                    "evidence": evidence,
                    "is_forecast": False,
                }
                self._observed[tid] = entry
                results.append(entry)
        return results

    def map_forecast(self, predicted_stage: str, probability: float) -> list[dict[str, Any]]:
        stage_to_techniques: dict[str, list[str]] = {
            "reconnaissance": ["T1595", "T1046"],
            "initial_access": ["T1190", "T1133"],
            "credential_access": ["T1110"],
            "lateral_movement": ["T1021", "T1570"],
            "command_and_control": ["T1071", "T1573"],
            "exfiltration": ["T1041", "T1048"],
            "impact": ["T1498", "T1499"],
        }
        technique_ids = stage_to_techniques.get(predicted_stage, [])
        results = []
        for tid in technique_ids:
            tech = self._techniques.get(tid)
            if tech:
                entry = {
                    "technique_id": tid,
                    "technique_name": tech["name"],
                    "tactic_id": tech["tactic"],
                    "tactic_name": self._tactics.get(tech["tactic"], {}).get("name", ""),
                    "probability": round(probability, 4),
                    "is_forecast": True,
                }
                self._forecast[tid] = entry
                results.append(entry)
        return results

    def get_matrix(self) -> dict[str, Any]:
        matrix: dict[str, list[dict]] = {}
        for tactic in MITRE_TACTICS:
            tactic_id = tactic["id"]
            techniques = [
                t for t in MITRE_TECHNIQUES if t["tactic"] == tactic_id
            ]
            matrix[tactic["name"]] = []
            for tech in techniques:
                entry = {
                    "id": tech["id"],
                    "name": tech["name"],
                    "observed": tech["id"] in self._observed,
                    "forecast": tech["id"] in self._forecast,
                    "confidence": self._observed.get(tech["id"], {}).get("confidence", 0),
                    "probability": self._forecast.get(tech["id"], {}).get("probability", 0),
                }
                matrix[tactic["name"]].append(entry)
        return {"tactics": MITRE_TACTICS, "matrix": matrix}

    def get_observed_techniques(self) -> list[dict]:
        return list(self._observed.values())

    def get_all_techniques(self) -> list[dict]:
        return MITRE_TECHNIQUES
