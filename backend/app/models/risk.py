from datetime import datetime, timezone
from sqlalchemy import String, DateTime, Float, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class RiskScore(Base):
    __tablename__ = "risk_scores"
    
    id: Mapped[str] = mapped_column(String, primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    
    host_id: Mapped[str] = mapped_column(String, ForeignKey("hosts.id"), index=True)
    
    total_score: Mapped[float] = mapped_column(Float, default=0.0)
    
    components: Mapped[dict] = mapped_column(JSONB, default=dict) # e.g., anomaly, forecast, signature, behavior, graph
