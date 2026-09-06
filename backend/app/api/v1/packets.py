"""Netra — Packets API (Wireshark-inspired)."""
from __future__ import annotations
from fastapi import APIRouter, Query
from typing import Any, Optional
router = APIRouter(prefix="/packets", tags=["packets"])

@router.get("/search")
async def search_packets(src_ip: Optional[str] = None, dst_ip: Optional[str] = None,
    protocol: Optional[str] = None, limit: int = Query(100, le=1000)) -> dict[str, Any]:
    return {"packets": [], "total": 0}

@router.get("/{packet_id}/decode")
async def decode_packet(packet_id: str) -> dict[str, Any]:
    return {"packet_id": packet_id, "layers": [], "hex": "", "ascii": ""}

@router.get("/pcap")
async def download_pcap(flow_id: Optional[str] = None, incident_id: Optional[str] = None) -> dict[str, Any]:
    return {"status": "no_pcap_available"}
