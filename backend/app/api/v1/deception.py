"""Netra — Deception API."""
from __future__ import annotations
from fastapi import APIRouter
from typing import Any
router = APIRouter(prefix="/deception", tags=["deception"])

@router.get("/honeypots")
async def get_honeypots() -> dict[str, Any]:
    return {"honeypots": [], "mode": "monitor_only"}

@router.get("/sessions")
async def get_honeypot_sessions() -> dict[str, Any]:
    return {"sessions": [], "total": 0}
