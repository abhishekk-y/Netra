from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime, Float
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class NormalizedEvent(Base):
    __tablename__ = "events"
    
    id: Mapped[str] = mapped_column(String, primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    sensor_id: Mapped[str] = mapped_column(String, index=True)
    event_type: Mapped[str] = mapped_column(String, index=True)
    
    source_ip: Mapped[str] = mapped_column(String, nullable=True, index=True)
    source_port: Mapped[int] = mapped_column(Integer, nullable=True)
    destination_ip: Mapped[str] = mapped_column(String, nullable=True, index=True)
    destination_port: Mapped[int] = mapped_column(Integer, nullable=True)
    protocol: Mapped[str] = mapped_column(String, nullable=True)
    
    community_id: Mapped[str] = mapped_column(String, nullable=True, index=True)
    flow_id: Mapped[str] = mapped_column(String, nullable=True, index=True)
    session_id: Mapped[str] = mapped_column(String, nullable=True)
    
    raw_source: Mapped[str] = mapped_column(String)  # e.g., 'zeek', 'suricata', 'pcap'
    severity: Mapped[int] = mapped_column(Integer, default=1)
    
    data: Mapped[dict] = mapped_column(JSONB, default=dict)
    evidence_reference: Mapped[str] = mapped_column(String, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
