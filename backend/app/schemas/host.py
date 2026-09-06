from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class HostBase(BaseModel):
    ip_address: Optional[str] = None
    mac_address: Optional[str] = None
    hostname: Optional[str] = None
    vendor: Optional[str] = None
    os: Optional[str] = None
    device_type: Optional[str] = None

class HostCreate(HostBase):
    id: str

class HostResponse(HostBase):
    id: str
    risk_score: float
    first_seen: datetime
    last_seen: datetime
    
    class Config:
        from_attributes = True

class HostDetail(HostResponse):
    services: List[Dict[str, Any]] = []
    tls_fingerprints: List[Dict[str, Any]] = []
    
    class Config:
        from_attributes = True
