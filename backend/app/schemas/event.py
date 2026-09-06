from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class NormalizedEventBase(BaseModel):
    timestamp: datetime
    sensor_id: str
    event_type: str
    source_ip: Optional[str] = None
    source_port: Optional[int] = None
    destination_ip: Optional[str] = None
    destination_port: Optional[int] = None
    protocol: Optional[str] = None
    community_id: Optional[str] = None
    flow_id: Optional[str] = None
    session_id: Optional[str] = None
    raw_source: str
    severity: int = 1
    confidence: float = 1.0

class NormalizedEventResponse(NormalizedEventBase):
    id: str
    data: Dict[str, Any] = {}
    evidence_reference: Optional[str] = None

    class Config:
        from_attributes = True
