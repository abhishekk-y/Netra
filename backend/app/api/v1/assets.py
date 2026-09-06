"""Netra — Assets API."""
from __future__ import annotations
from fastapi import APIRouter, Body
from typing import Any, Optional
router = APIRouter(prefix="/assets", tags=["assets"])

@router.get("")
async def get_assets(criticality: Optional[str] = None) -> dict[str, Any]:
    return {"assets": [], "total": 0}

@router.patch("/{asset_id}")
async def update_asset(asset_id: str, data: dict = Body(...)) -> dict[str, Any]:
    return {"id": asset_id, "updated": True}
