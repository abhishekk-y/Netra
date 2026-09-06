from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime, Float, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class Flow(Base):
    __tablename__ = "flows"
    
    id: Mapped[str] = mapped_column(String, primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    sensor_id: Mapped[str] = mapped_column(String, index=True)
    community_id: Mapped[str] = mapped_column(String, index=True)
    flow_id: Mapped[str] = mapped_column(String, index=True)
    
    src_ip: Mapped[str] = mapped_column(String, index=True)
    dst_ip: Mapped[str] = mapped_column(String, index=True)
    src_port: Mapped[int] = mapped_column(Integer, index=True)
    dst_port: Mapped[int] = mapped_column(Integer, index=True)
    
    protocol: Mapped[str] = mapped_column(String)
    app_protocol: Mapped[str] = mapped_column(String, nullable=True)
    
    packets_forward: Mapped[int] = mapped_column(Integer, default=0)
    packets_backward: Mapped[int] = mapped_column(Integer, default=0)
    bytes_forward: Mapped[int] = mapped_column(Integer, default=0)
    bytes_backward: Mapped[int] = mapped_column(Integer, default=0)
    duration_ms: Mapped[int] = mapped_column(Integer, default=0)
    
    tcp_flags: Mapped[dict] = mapped_column(JSONB, default=dict)
    flow_features: Mapped[dict] = mapped_column(JSONB, default=dict)
    
    risk_score: Mapped[float] = mapped_column(Float, default=0.0)
    anomaly_score: Mapped[float] = mapped_column(Float, default=0.0)
    attack_type: Mapped[str] = mapped_column(String, nullable=True)
    attack_confidence: Mapped[float] = mapped_column(Float, default=0.0)
    
    src_host_id: Mapped[str] = mapped_column(String, ForeignKey("hosts.id"), nullable=True)
    dst_host_id: Mapped[str] = mapped_column(String, ForeignKey("hosts.id"), nullable=True)
    
    incident_id: Mapped[str] = mapped_column(String, ForeignKey("incidents.id"), nullable=True)
    pcap_reference: Mapped[str] = mapped_column(String, nullable=True)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)
