from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class DNSRecord(Base):
    __tablename__ = "dns_records"
    
    id: Mapped[str] = mapped_column(String, primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    
    client_ip: Mapped[str] = mapped_column(String, index=True)
    server_ip: Mapped[str] = mapped_column(String, index=True)
    query: Mapped[str] = mapped_column(String, index=True)
    qtype: Mapped[str] = mapped_column(String)
    
    rcode: Mapped[str] = mapped_column(String, nullable=True)
    answers: Mapped[dict] = mapped_column(JSONB, default=list)
    ttl: Mapped[int] = mapped_column(Integer, nullable=True)
    
    community_id: Mapped[str] = mapped_column(String, nullable=True, index=True)
