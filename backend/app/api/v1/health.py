"""Netra — Health API."""
from __future__ import annotations
from fastapi import APIRouter
from typing import Any
router = APIRouter(prefix="/health", tags=["health"])

@router.get("")
async def get_health() -> dict[str, Any]:
    from ...services.health.health_monitor import HealthMonitor
    monitor = HealthMonitor()
    return monitor.get_system_health()

@router.get("/sensors")
async def get_sensor_metrics() -> dict[str, Any]:
    from ...services.health.health_monitor import HealthMonitor
    monitor = HealthMonitor()
    return monitor.get_sensor_metrics()
