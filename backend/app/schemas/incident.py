from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class IncidentBase(BaseModel):
    title: str
    description: str
    severity: str = "Low"
    primary_threat_actor: Optional[str] = None

class IncidentCreate(IncidentBase):
    pass

class IncidentUpdate(BaseModel):
    status: Optional[str] = None
    severity: Optional[str] = None
    assignee_id: Optional[str] = None
    resolved_at: Optional[datetime] = None

class EvidenceGraph(BaseModel):
    nodes: List[Dict[str, Any]] = []
    edges: List[Dict[str, Any]] = []

class IncidentResponse(IncidentBase):
    id: str
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None
    status: str
    assignee_id: Optional[str] = None

    class Config:
        from_attributes = True

class IncidentDetail(IncidentResponse):
    attack_stages: List[str] = []
    affected_hosts: List[str] = []
    indicators: List[Dict[str, Any]] = []
    evidence_graph: Dict[str, Any] = {}
    recommended_actions: List[str] = []
    notes: List[Dict[str, Any]] = []

    class Config:
        from_attributes = True
