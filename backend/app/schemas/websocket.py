from pydantic import BaseModel
from typing import Dict, Any, Optional

class WSMessage(BaseModel):
    type: str  # e.g., 'subscribe', 'unsubscribe', 'event'
    channel: Optional[str] = None
    payload: Dict[str, Any] = {}

class WSSubscription(BaseModel):
    channel: str  # telemetry, topology, alerts, incidents, forecast, risk, health
