from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class AlertBase(BaseModel):
    timestamp: datetime
    rule_id: str
    name: str
    description: str
    severity: str
    category: str
    src_ip: Optional[str] = None
    dst_ip: Optional[str] = None
    community_id: Optional[str] = None
    score: float = 0.0
    confidence: float = 1.0
    mitre_tactic: Optional[str] = None
    mitre_technique: Optional[str] = None
    status: str = "new"

class AlertResponse(AlertBase):
    id: str
    incident_id: Optional[str] = None

    class Config:
        from_attributes = True

class AlertDetail(AlertResponse):
    evidence: Dict[str, Any] = {}

    class Config:
        from_attributes = True
