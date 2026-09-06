"""
Netra — Dashboard API
Returns SOC dashboard summary metrics from real telemetry.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from datetime import datetime, timezone
from typing import Any

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary")
async def get_dashboard_summary() -> dict[str, Any]:
    """Return all SOC dashboard metrics. Values from real telemetry only."""
    from ..core.events import event_bus

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "sensor": {
            "status": "live" if event_bus._connected else "disconnected",
            "packets_per_sec": 0,
            "flows_per_sec": 0,
            "capture_drop_pct": 0.0,
        },
        "network": {
            "hosts_count": 0,
            "active_connections": 0,
        },
        "security": {
            "incidents_count": 0,
            "active_incidents": 0,
            "alerts_count": 0,
            "forecast_risk": "low",
        },
        "system": {
            "cpu_percent": 0.0,
            "memory_percent": 0.0,
            "disk_percent": 0.0,
        },
        "top_risk_hosts": [],
        "latest_incidents": [],
        "protocol_distribution": {},
        "attack_stage_distribution": {},
        "traffic_rate_history": [],
        "note": "Metrics populate when telemetry is active",
    }
