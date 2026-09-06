from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime, Float, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class Forecast(Base):
    __tablename__ = "forecasts"
    
    id: Mapped[str] = mapped_column(String, primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    
    host_id: Mapped[str] = mapped_column(String, ForeignKey("hosts.id"), index=True)
    current_state: Mapped[str] = mapped_column(String)
    
    predictions: Mapped[dict] = mapped_column(JSONB, default=list) # List of StagePrediction
    target_predictions: Mapped[dict] = mapped_column(JSONB, default=list) # List of TargetPrediction
    uncertainty: Mapped[dict] = mapped_column(JSONB, default=dict)
    explanation: Mapped[dict] = mapped_column(JSONB, default=dict)
    
    time_horizon_sec: Mapped[int] = mapped_column(Integer, default=3600)
    
    actual_outcome: Mapped[str] = mapped_column(String, nullable=True) # Populated later for vs Actual
