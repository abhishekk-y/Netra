from datetime import datetime, timezone
from sqlalchemy import String, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class TLSRecord(Base):
    __tablename__ = "tls_records"
    
    id: Mapped[str] = mapped_column(String, primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    
    client_ip: Mapped[str] = mapped_column(String, index=True)
    server_ip: Mapped[str] = mapped_column(String, index=True)
    
    version: Mapped[str] = mapped_column(String, nullable=True)
    cipher: Mapped[str] = mapped_column(String, nullable=True)
    server_name: Mapped[str] = mapped_column(String, nullable=True, index=True)
    
    ja4_fingerprint: Mapped[str] = mapped_column(String, nullable=True, index=True)
    certificate_chain_hashes: Mapped[dict] = mapped_column(JSONB, default=list)
    
    community_id: Mapped[str] = mapped_column(String, nullable=True, index=True)
