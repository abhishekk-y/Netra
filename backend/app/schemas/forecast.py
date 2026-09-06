from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class StagePrediction(BaseModel):
    stage: str
    probability: float
    time_to_stage_sec: Optional[int] = None

class TargetPrediction(BaseModel):
    target_host_id: str
    probability: float

class ForecastExplanation(BaseModel):
    contributing_factors: List[str]
    historical_precedence: float
    model_confidence: float

class ForecastBase(BaseModel):
    timestamp: datetime
    host_id: str
    current_state: str
    time_horizon_sec: int

class ForecastResponse(ForecastBase):
    id: str
    predictions: List[StagePrediction] = []
    target_predictions: List[TargetPrediction] = []
    uncertainty: Dict[str, Any] = {}
    explanation: Dict[str, Any] = {}
    actual_outcome: Optional[str] = None

    class Config:
        from_attributes = True

class ForecastVsActual(BaseModel):
    forecast_id: str
    predicted_state: str
    actual_state: str
    accuracy_score: float
    timestamp: datetime
