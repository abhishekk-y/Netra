"""
Netra — Incident Manager
Creates, updates, and manages incidents from correlated detections.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Optional
from enum import Enum


class IncidentStatus(str, Enum):
    NEW = "new"
    TRIAGED = "triaged"
    INVESTIGATING = "investigating"
    CONTAINED = "contained"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"


class IncidentSeverity(str, Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


RESPONSE_RECOMMENDATIONS: dict[str, list[str]] = {
    "reconnaissance": [
        "Observe and monitor source activity",
        "Increase capture fidelity for source host",
        "Review firewall logs for scan patterns",
        "Consider blocking if persistent",
    ],
    "credential_access": [
        "Review authentication logs on target",
        "Enforce account lockout policies",
        "Check for compromised credentials",
        "Increase monitoring on target services",
        "Capture PCAP for forensic evidence",
    ],
    "initial_access": [
        "Isolate affected host if in lab environment",
        "Review web application logs",
        "Check for known exploit signatures",
        "Capture full PCAP evidence",
        "Block known IOCs",
    ],
    "lateral_movement": [
        "Review east-west traffic patterns",
        "Check for unauthorized SMB/SSH/RDP usage",
        "Isolate affected subnet if authorized",
        "Review adjacent host integrity",
        "Capture PCAP of lateral communications",
    ],
    "command_and_control": [
        "Analyze beaconing patterns",
        "Block C2 indicators at firewall",
        "Capture full session data",
        "Review DNS queries for DGA patterns",
        "Consider network isolation",
    ],
    "exfiltration": [
        "Monitor outbound data volumes",
        "Review large file transfers",
        "Block suspicious destinations",
        "Capture all outbound PCAP",
        "Escalate to incident response team",
    ],
    "impact": [
        "Isolate affected systems immediately",
        "Preserve all forensic evidence",
        "Activate incident response plan",
        "Notify stakeholders",
        "Begin recovery procedures",
    ],
}


class Incident:
    """A security incident composed of correlated alerts and evidence."""

    def __init__(self, title: str, severity: str = "medium"):
        self.id = str(uuid.uuid4())
        self.number = 0
        self.title = title
        self.status = IncidentStatus.NEW
        self.severity = IncidentSeverity(severity) if severity in [e.value for e in IncidentSeverity] else IncidentSeverity.MEDIUM
        self.confidence: float = 0.0
        self.current_stage: Optional[str] = None
        self.forecast_stages: list[dict] = []
        self.affected_hosts: list[dict] = []
        self.affected_host_ids: set[str] = set()
        self.alerts: list[dict] = []
        self.flows: list[str] = []
        self.sessions: list[str] = []
        self.pcap_references: list[str] = []
        self.mitre_tactics: list[str] = []
        self.mitre_techniques: list[dict] = []
        self.evidence_summary: dict = {}
        self.blast_radius: dict = {}
        self.attack_path: list[dict] = []
        self.analyst_notes: str = ""
        self.recommended_actions: list[str] = []
        self.timeline: list[dict] = []
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
        self.resolved_at: Optional[datetime] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "number": self.number,
            "title": self.title,
            "status": self.status.value,
            "severity": self.severity.value,
            "confidence": round(self.confidence, 4),
            "current_stage": self.current_stage,
            "forecast_stages": self.forecast_stages,
            "affected_hosts": self.affected_hosts,
            "alerts_count": len(self.alerts),
            "flows_count": len(self.flows),
            "mitre_tactics": self.mitre_tactics,
            "mitre_techniques": self.mitre_techniques,
            "blast_radius": self.blast_radius,
            "attack_path": self.attack_path,
            "recommended_actions": self.recommended_actions,
            "analyst_notes": self.analyst_notes,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
        }

    def to_detail_dict(self) -> dict[str, Any]:
        d = self.to_dict()
        d["alerts"] = self.alerts[-100:]
        d["flows"] = self.flows[-100:]
        d["sessions"] = self.sessions[-50:]
        d["pcap_references"] = self.pcap_references
        d["evidence_summary"] = self.evidence_summary
        d["timeline"] = self.timeline[-200:]
        return d


class IncidentManager:
    """Manages incident lifecycle from creation through resolution."""

    def __init__(self):
        self._incidents: dict[str, Incident] = {}
        self._counter = 0

    def create_incident(
        self,
        title: str,
        severity: str = "medium",
        alerts: Optional[list[dict]] = None,
        affected_hosts: Optional[list[dict]] = None,
        attack_stage: Optional[str] = None,
        confidence: float = 0.0,
    ) -> Incident:
        self._counter += 1
        incident = Incident(title, severity)
        incident.number = self._counter
        incident.confidence = confidence
        incident.current_stage = attack_stage

        if alerts:
            for alert in alerts:
                incident.alerts.append(alert)
                community_id = alert.get("community_id")
                if community_id:
                    incident.flows.append(community_id)

        if affected_hosts:
            for host in affected_hosts:
                host_id = host.get("host_id", host.get("ip", ""))
                if host_id not in incident.affected_host_ids:
                    incident.affected_hosts.append(host)
                    incident.affected_host_ids.add(host_id)

        if attack_stage:
            recommendations = RESPONSE_RECOMMENDATIONS.get(attack_stage, [])
            incident.recommended_actions = recommendations

        incident.timeline.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": "incident_created",
            "description": f"Incident created: {title}",
            "stage": attack_stage,
        })

        self._incidents[incident.id] = incident
        return incident

    def update_incident(self, incident_id: str, updates: dict[str, Any]) -> Optional[Incident]:
        incident = self._incidents.get(incident_id)
        if not incident:
            return None

        if "status" in updates:
            try:
                new_status = IncidentStatus(updates["status"])
                old_status = incident.status
                incident.status = new_status
                incident.timeline.append({
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "event": "status_change",
                    "description": f"Status: {old_status.value} -> {new_status.value}",
                })
                if new_status == IncidentStatus.RESOLVED:
                    incident.resolved_at = datetime.now(timezone.utc)
            except ValueError:
                pass

        if "severity" in updates:
            try:
                incident.severity = IncidentSeverity(updates["severity"])
            except ValueError:
                pass

        if "analyst_notes" in updates:
            incident.analyst_notes = updates["analyst_notes"]

        if "title" in updates:
            incident.title = updates["title"]

        incident.updated_at = datetime.now(timezone.utc)
        return incident

    def add_alert_to_incident(self, incident_id: str, alert: dict) -> bool:
        incident = self._incidents.get(incident_id)
        if not incident:
            return False
        incident.alerts.append(alert)
        incident.updated_at = datetime.now(timezone.utc)
        incident.timeline.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": "alert_added",
            "description": f"Alert: {alert.get('signature', 'Unknown')}",
        })
        src_ip = alert.get("src_ip")
        if src_ip and src_ip not in incident.affected_host_ids:
            incident.affected_hosts.append({"ip": src_ip})
            incident.affected_host_ids.add(src_ip)
        return True

    def add_forecast_to_incident(self, incident_id: str, forecast: dict) -> bool:
        incident = self._incidents.get(incident_id)
        if not incident:
            return False
        incident.forecast_stages = forecast.get("predictions", [])
        incident.current_stage = forecast.get("current_stage")
        if forecast.get("current_stage"):
            recommendations = RESPONSE_RECOMMENDATIONS.get(forecast["current_stage"], [])
            incident.recommended_actions = recommendations
        incident.updated_at = datetime.now(timezone.utc)
        incident.timeline.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": "forecast_updated",
            "description": f"Stage: {forecast.get('current_stage')}",
        })
        return True

    def get_incident(self, incident_id: str) -> Optional[dict]:
        incident = self._incidents.get(incident_id)
        return incident.to_detail_dict() if incident else None

    def get_incidents(self, status: Optional[str] = None, limit: int = 50) -> list[dict]:
        incidents = list(self._incidents.values())
        if status:
            incidents = [i for i in incidents if i.status.value == status]
        incidents.sort(key=lambda x: x.created_at, reverse=True)
        return [i.to_dict() for i in incidents[:limit]]

    def get_active_incidents(self) -> list[dict]:
        active = [
            i for i in self._incidents.values()
            if i.status not in (IncidentStatus.RESOLVED, IncidentStatus.FALSE_POSITIVE)
        ]
        active.sort(key=lambda x: x.created_at, reverse=True)
        return [i.to_dict() for i in active]

    def get_incident_count(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for incident in self._incidents.values():
            s = incident.status.value
            counts[s] = counts.get(s, 0) + 1
        counts["total"] = len(self._incidents)
        return counts

    def get_replay_data(self, incident_id: str) -> Optional[dict]:
        incident = self._incidents.get(incident_id)
        if not incident:
            return None
        return {
            "incident_id": incident.id,
            "title": incident.title,
            "timeline": incident.timeline,
            "alerts": incident.alerts,
            "affected_hosts": incident.affected_hosts,
            "attack_path": incident.attack_path,
            "forecast_stages": incident.forecast_stages,
            "created_at": incident.created_at.isoformat(),
            "resolved_at": incident.resolved_at.isoformat() if incident.resolved_at else None,
        }
