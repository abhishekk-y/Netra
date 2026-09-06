from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime, Float
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class HoneypotSession(Base):
    __tablename__ = "honeypot_sessions"
    
    id: Mapped[str] = mapped_column(String, primary_key=True)
    start_time: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    end_time: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    
    attacker_ip: Mapped[str] = mapped_column(String, index=True)
    honeypot_ip: Mapped[str] = mapped_column(String, index=True)
    honeypot_profile: Mapped[str] = mapped_column(String)
    
    protocol: Mapped[str] = mapped_column(String)
    port: Mapped[int] = mapped_column(Integer)
    
    credentials_tried: Mapped[dict] = mapped_column(JSONB, default=list)
    commands_executed: Mapped[dict] = mapped_column(JSONB, default=list)
    files_dropped: Mapped[dict] = mapped_column(JSONB, default=list)
    
    community_id: Mapped[str] = mapped_column(String, nullable=True, index=True)
