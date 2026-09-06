"""Netra — Flows API endpoints."""
from __future__ import annotations
from fastapi import APIRouter, Query
from typing import Any, Optional
router = APIRouter(prefix="/flows", tags=["flows"])

@router.get("")
async def get_flows(
    src_ip: Optional[str] = None, dst_ip: Optional[str] = None,
    protocol: Optional[str] = None, min_risk: Optional[float] = None,
    limit: int = Query(100, le=1000), offset: int = 0,
) -> dict[str, Any]:
    return {"flows": [], "total": 0, "limit": limit, "offset": offset}

@router.get("/{flow_id}")
async def get_flow(flow_id: str) -> dict[str, Any]:
    return {"flow_id": flow_id, "features": {}, "alerts": [], "timeline": []}

@router.get("/{flow_id}/packets")
async def get_flow_packets(flow_id: str, limit: int = 100) -> dict[str, Any]:
    return {"flow_id": flow_id, "packets": [], "total": 0}
