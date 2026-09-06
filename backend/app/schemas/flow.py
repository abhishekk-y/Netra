from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class FlowBase(BaseModel):
    timestamp: datetime
    sensor_id: str
    community_id: str
    flow_id: str
    src_ip: str
    dst_ip: str
    src_port: int
    dst_port: int
    protocol: str
    app_protocol: Optional[str] = None
    packets_forward: int = 0
    packets_backward: int = 0
    bytes_forward: int = 0
    bytes_backward: int = 0
    duration_ms: int = 0

class FlowFeatures(BaseModel):
    # Typical ML features
    mean_pkt_len_fwd: float = 0.0
    mean_pkt_len_bwd: float = 0.0
    flow_bytes_s: float = 0.0
    flow_pkts_s: float = 0.0

class FlowFilter(BaseModel):
    src_ip: Optional[str] = None
    dst_ip: Optional[str] = None
    port: Optional[int] = None
    protocol: Optional[str] = None

class FlowResponse(FlowBase):
    id: str
    risk_score: float
    anomaly_score: float
    attack_type: Optional[str] = None
    attack_confidence: float
    
    class Config:
        from_attributes = True

class FlowDetail(FlowResponse):
    tcp_flags: Dict[str, Any] = {}
    flow_features: Dict[str, Any] = {}
    src_host_id: Optional[str] = None
    dst_host_id: Optional[str] = None
    incident_id: Optional[str] = None
    pcap_reference: Optional[str] = None
    metadata_: Dict[str, Any] = {}
    
    class Config:
        from_attributes = True
