from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime, Float, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class TopologyNode(Base):
    __tablename__ = "topology_nodes"
    
    id: Mapped[str] = mapped_column(String, primary_key=True) # same as host_id or subnet_id
    type: Mapped[str] = mapped_column(String) # host, subnet, router, switch
    label: Mapped[str] = mapped_column(String)
    properties: Mapped[dict] = mapped_column(JSONB, default=dict)
    layer: Mapped[str] = mapped_column(String, nullable=True) # core, distribution, access, endpoint
    zone: Mapped[str] = mapped_column(String, nullable=True)

class TopologyEdge(Base):
    __tablename__ = "topology_edges"
    
    id: Mapped[str] = mapped_column(String, primary_key=True)
    source_id: Mapped[str] = mapped_column(String, ForeignKey("topology_nodes.id"), index=True)
    target_id: Mapped[str] = mapped_column(String, ForeignKey("topology_nodes.id"), index=True)
    type: Mapped[str] = mapped_column(String) # l2_link, l3_route, logical_flow
    
    first_seen: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_seen: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    metrics: Mapped[dict] = mapped_column(JSONB, default=dict) # bandwidth, latency, packets

class TopologySnapshot(Base):
    __tablename__ = "topology_snapshots"
    
    id: Mapped[str] = mapped_column(String, primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    nodes: Mapped[dict] = mapped_column(JSONB, default=list)
    edges: Mapped[dict] = mapped_column(JSONB, default=list)
    is_incident_trigger: Mapped[bool] = mapped_column(Boolean, default=False)
