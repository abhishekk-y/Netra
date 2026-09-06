from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta
import uuid

from app.models.alert import Alert
from app.schemas.incident import IncidentCreate

class IncidentCandidate:
    def __init__(self):
        self.id = str(uuid.uuid4())
        self.alerts: List[Alert] = []
        self.hosts: set = set()
        self.community_ids: set = set()
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.score: float = 0.0

class CorrelationEngine:
    def __init__(self, time_window_sec: int = 300):
        self.time_window = timedelta(seconds=time_window_sec)
        self.recent_alerts: List[Alert] = []
        
    def add_alert(self, alert: Alert) -> None:
        self.recent_alerts.append(alert)
        self._prune_old_alerts(alert.timestamp)
        
    def _prune_old_alerts(self, current_time: datetime) -> None:
        cutoff = current_time - self.time_window
        self.recent_alerts = [a for a in self.recent_alerts if a.timestamp >= cutoff]
        
    def correlate(self) -> List[IncidentCandidate]:
        candidates: List[IncidentCandidate] = []
        
        # Simple clustering algorithm based on shared hosts or community IDs
        for alert in self.recent_alerts:
            matched = False
            for candidate in candidates:
                if (alert.src_ip in candidate.hosts or 
                    alert.dst_ip in candidate.hosts or 
                    (alert.community_id and alert.community_id in candidate.community_ids)):
                    
                    candidate.alerts.append(alert)
                    if alert.src_ip: candidate.hosts.add(alert.src_ip)
                    if alert.dst_ip: candidate.hosts.add(alert.dst_ip)
                    if alert.community_id: candidate.community_ids.add(alert.community_id)
                    candidate.end_time = max(candidate.end_time, alert.timestamp)
                    candidate.score += alert.score
                    matched = True
                    break
                    
            if not matched:
                new_cand = IncidentCandidate()
                new_cand.alerts.append(alert)
                if alert.src_ip: new_cand.hosts.add(alert.src_ip)
                if alert.dst_ip: new_cand.hosts.add(alert.dst_ip)
                if alert.community_id: new_cand.community_ids.add(alert.community_id)
                new_cand.start_time = alert.timestamp
                new_cand.end_time = alert.timestamp
                new_cand.score = alert.score
                candidates.append(new_cand)
                
        # Filter out candidates that are just single low-severity alerts
        valid_candidates = [c for c in candidates if len(c.alerts) > 1 or c.score > 50.0]
        return valid_candidates
