from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime, Float, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class Alert(Base):
    __tablename__ = "alerts"
    
    id: Mapped[str] = mapped_column(String, primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    
    rule_id: Mapped[str] = mapped_column(String, index=True)
    name: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
    severity: Mapped[str] = mapped_column(String) # low, medium, high, critical
    category: Mapped[str] = mapped_column(String)
    
    src_ip: Mapped[str] = mapped_column(String, nullable=True, index=True)
    dst_ip: Mapped[str] = mapped_column(String, nullable=True, index=True)
    community_id: Mapped[str] = mapped_column(String, nullable=True, index=True)
    
    score: Mapped[float] = mapped_column(Float, default=0.0)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    
    mitre_tactic: Mapped[str] = mapped_column(String, nullable=True)
    mitre_technique: Mapped[str] = mapped_column(String, nullable=True)
    
    evidence: Mapped[dict] = mapped_column(JSONB, default=dict)
    incident_id: Mapped[str] = mapped_column(String, ForeignKey("incidents.id"), nullable=True)
    
    status: Mapped[str] = mapped_column(String, default="new") # new, associated, dismissed
