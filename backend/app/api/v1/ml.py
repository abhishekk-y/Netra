"""ML API endpoints — inference, status, and on-demand prediction."""
from __future__ import annotations
from fastapi import APIRouter, Request
from typing import Any

router = APIRouter(prefix="/ml", tags=["ml"])

try:
    from app.ml_inference import predict_flow, get_model_status
except ImportError:
    def predict_flow(flow): return {'mlAvailable': False}
    def get_model_status(): return {'available': False}


@router.get("/status")
def ml_status() -> dict:
    """Return ML ensemble metadata and loaded status."""
    return get_model_status()


@router.post("/predict")
async def ml_predict(request: Request) -> dict:
    """
    Run ML inference on a single flow dict.
    Body: { srcIp, dstIp, srcPort, dstPort, protocol, bytes, packets, duration }
    """
    body: dict[str, Any] = await request.json()
    return predict_flow(body)
