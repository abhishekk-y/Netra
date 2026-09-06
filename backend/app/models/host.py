from sqlalchemy import Column, String, Integer, DateTime, JSON, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base

class Host(Base):
    __tablename__ = "hosts"
    
    id = Column(String, primary_key=True, index=True) # Could be MAC or generated UUID
    ip_address = Column(String, index=True)
    mac_address = Column(String, index=True)
    hostname = Column(String)
    vendor = Column(String)
    os = Column(String)
    device_type = Column(String)
    
    # JSON fields for complex data
    services = Column(JSON, default=list) # List of observed services
    tls_fingerprints = Column(JSON, default=list)
    
    first_seen = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_seen = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    risk_score = Column(Float, default=0.0)
    
    baselines = relationship("HostBaseline", back_populates="host", cascade="all, delete-orphan")

class HostBaseline(Base):
    __tablename__ = "host_baselines"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    host_id = Column(String, ForeignKey("hosts.id"))
    window_size = Column(String) # e.g., "1h", "24h"
    
    connections_per_sec = Column(Float)
    unique_peers = Column(Integer)
    bandwidth_in = Column(Float)
    bandwidth_out = Column(Float)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    host = relationship("Host", back_populates="baselines")
