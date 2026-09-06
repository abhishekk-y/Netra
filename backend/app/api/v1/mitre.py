"""Netra — MITRE ATT&CK API."""
from __future__ import annotations
from fastapi import APIRouter
from typing import Any
router = APIRouter(prefix="/mitre", tags=["mitre"])

@router.get("/matrix")
async def get_matrix() -> dict[str, Any]:
    from ...services.mitre.attack_mapper import ATTACKMapper
    mapper = ATTACKMapper()
    return mapper.get_matrix()

@router.get("/techniques")
async def get_techniques() -> dict[str, Any]:
    from ...services.mitre.attack_mapper import MITRE_TECHNIQUES
    return {"techniques": MITRE_TECHNIQUES, "total": len(MITRE_TECHNIQUES)}
