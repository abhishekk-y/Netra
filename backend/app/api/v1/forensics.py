"""Netra — Forensics API."""
from __future__ import annotations
from fastapi import APIRouter
from typing import Any
router = APIRouter(prefix="/forensics", tags=["forensics"])

@router.get("/evidence/{incident_id}")
async def get_evidence(incident_id: str) -> dict[str, Any]:
    return {"incident_id": incident_id, "evidence_graph": {"nodes": [], "edges": []}, "pcap_references": [], "integrity": []}

@router.get("/replay/{incident_id}")
async def get_replay(incident_id: str) -> dict[str, Any]:
    return {"incident_id": incident_id, "frames": [], "duration_ms": 0}
