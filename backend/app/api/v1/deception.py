"""Netra — Deception API."""
from __future__ import annotations
from fastapi import APIRouter
from typing import Any
import random
from datetime import datetime, timezone

router = APIRouter(prefix="/deception", tags=["deception"])

_HONEYPOTS = []
_INIT_DONE = False

def _init_deception():
    global _INIT_DONE
    if _INIT_DONE:
        return
    for i in range(30):
        _HONEYPOTS.append({
            "id": f"hp-{i}",
            "x": random.uniform(0, 100),
            "y": random.uniform(0, 100),
            "value": random.uniform(5, 50),
            "isHuman": random.random() > 0.8
        })
    _INIT_DONE = True

_init_deception()

@router.get("/honeypots")
async def get_honeypots() -> dict[str, Any]:
    return {"honeypots": _HONEYPOTS, "mode": "active_engagement"}

@router.get("/sessions")
async def get_honeypot_sessions() -> dict[str, Any]:
    return {"sessions": [], "total": 0}
