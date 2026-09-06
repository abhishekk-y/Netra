"""Netra — Settings API."""
from __future__ import annotations
from fastapi import APIRouter, Body
from typing import Any
router = APIRouter(prefix="/settings", tags=["settings"])

DEFAULT_FLAGS = {
    "FEATURE_ZEEK": True, "FEATURE_SURICATA": False, "FEATURE_ARKIME": False,
    "FEATURE_HONEYPOT": False, "FEATURE_EBPF": False, "FEATURE_GNN": False,
    "FEATURE_LLM": False, "FEATURE_NETBOX": False, "FEATURE_KUBERNETES": False,
    "FEATURE_THREAT_INTEL": False, "FEATURE_IPFIX": False,
}

@router.get("/features")
async def get_features() -> dict[str, Any]:
    return {"features": DEFAULT_FLAGS}

@router.patch("/features")
async def toggle_feature(data: dict = Body(...)) -> dict[str, Any]:
    return {"updated": True, "features": DEFAULT_FLAGS}
