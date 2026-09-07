"""Netra — Topology API endpoints."""
from __future__ import annotations
from fastapi import APIRouter, Query
from datetime import datetime, timezone
from typing import Any
import random

router = APIRouter(prefix="/topology", tags=["topology"])

# Generate a persistent in-memory dense topology graph
_TOPOLOGY = {"nodes": [], "edges": []}
_INIT_DONE = False

def _init_topology():
    global _INIT_DONE
    if _INIT_DONE:
        return
        
    core_count = 4
    dist_count = 12
    edge_count = 60
    
    # Core
    for i in range(core_count):
        _TOPOLOGY["nodes"].append({
            "data": { "id": f"core-{i}", "label": f"WAN_GW_{i}", "type": "CORE", "ip": f"1.1.1.{i+1}", "risk": random.uniform(5, 20), "model": "Cisco ASR 9000", "fw": "IOS XR 7.3" }
        })
        
    # Distribution
    for i in range(dist_count):
        _TOPOLOGY["nodes"].append({
            "data": { "id": f"dist-{i}", "label": f"FW_AG_{i}", "type": "FIREWALL", "ip": f"10.0.0.{i+1}", "risk": random.uniform(10, 40), "model": "Palo Alto PA-5250", "fw": "PAN-OS 10.1" }
        })
        _TOPOLOGY["edges"].append({"data": {"source": f"core-{i % core_count}", "target": f"dist-{i}", "type": "TRUNK"}})
        
    # Edge
    for i in range(edge_count):
        is_critical = random.random() > 0.9
        _TOPOLOGY["nodes"].append({
            "data": { 
                "id": f"edge-{i}", "label": f"SRV_ND_{i}", "type": "DB" if is_critical else "COMPUTE", "ip": f"10.0.1.{i+10}", 
                "risk": random.uniform(80, 100) if is_critical else random.uniform(5, 50),
                "model": "Oracle Exadata" if is_critical else "Dell PowerEdge R740",
                "fw": "Linux 5.15"
            }
        })
        _TOPOLOGY["edges"].append({"data": {"source": f"dist-{i % dist_count}", "target": f"edge-{i}", "type": "ACCESS"}})
        
    # Cross-links
    for i in range(15):
        _TOPOLOGY["edges"].append({"data": {"source": f"edge-{random.randint(0, edge_count-1)}", "target": f"edge-{random.randint(0, edge_count-1)}", "type": "PEER"}})
        
    _INIT_DONE = True

_init_topology()


@router.get("/graph")
async def get_topology_graph(
    view: str = Query("physical", description="View mode: physical/l2/l3/logical/security/attack/forensic/forecast/vlan/subnet/asset"),
    layout: str = Query("hierarchical", description="Layout: hierarchical/force/radial/tree"),
) -> dict[str, Any]:
    return {
        "nodes": _TOPOLOGY["nodes"],
        "edges": _TOPOLOGY["edges"],
        "view": view, 
        "layout": layout, 
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@router.get("/snapshot/{timestamp}")
async def get_topology_snapshot(timestamp: str) -> dict[str, Any]:
    return {"nodes": [], "edges": [], "snapshot_time": timestamp}

@router.get("/diff")
async def get_topology_diff(
    from_ts: str = Query(..., description="Start timestamp"),
    to_ts: str = Query(..., description="End timestamp"),
) -> dict[str, Any]:
    return {"new_nodes": [], "removed_nodes": [], "new_edges": [], "removed_edges": [], "from": from_ts, "to": to_ts}

@router.get("/path")
async def get_path_analysis(
    src: str = Query(..., description="Source IP"),
    dst: str = Query(..., description="Destination IP"),
) -> dict[str, Any]:
    return {"source": src, "destination": dst, "hops": [], "total_latency_ms": 0, "risk": 0}
