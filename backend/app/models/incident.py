from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime, Float, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class Incident(Base):
    __tablename__ = "incidents"
    
    id: Mapped[str] = mapped_column(String, primary_key=True)
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(Text)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    resolved_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    
    status: Mapped[str] = mapped_column(String, default="New") # New, Triaged, Investigating, Contained, Resolved, FalsePositive
    severity: Mapped[str] = mapped_column(String, default="Low") # Low, Medium, High, Critical
    
    assignee_id: Mapped[str] = mapped_column(String, nullable=True)
    
    primary_threat_actor: Mapped[str] = mapped_column(String, nullable=True)
    attack_stages: Mapped[dict] = mapped_column(JSONB, default=list) # List of identified stages
    
    affected_hosts: Mapped[dict] = mapped_column(JSONB, default=list)
    indicators: Mapped[dict] = mapped_column(JSONB, default=list)
    evidence_graph: Mapped[dict] = mapped_column(JSONB, default=dict)
    
    recommended_actions: Mapped[dict] = mapped_column(JSONB, default=list)
    notes: Mapped[dict] = mapped_column(JSONB, default=list)
