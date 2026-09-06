"""
Netra — Health Monitor
Monitors all platform components and reports system health.
"""
from __future__ import annotations

import os
import time
import platform
from datetime import datetime, timezone
from typing import Any, Optional


class ComponentHealth:
    """Health status for a single component."""

    def __init__(self, name: str):
        self.name = name
        self.status: str = "unknown"
        self.last_check: Optional[datetime] = None
        self.metrics: dict[str, Any] = {}
        self.error: Optional[str] = None

    def set_healthy(self, metrics: Optional[dict] = None) -> None:
        self.status = "healthy"
        self.last_check = datetime.now(timezone.utc)
        self.metrics = metrics or {}
        self.error = None

    def set_degraded(self, reason: str, metrics: Optional[dict] = None) -> None:
        self.status = "degraded"
        self.last_check = datetime.now(timezone.utc)
        self.metrics = metrics or {}
        self.error = reason

    def set_down(self, reason: str) -> None:
        self.status = "down"
        self.last_check = datetime.now(timezone.utc)
        self.error = reason

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status,
            "last_check": self.last_check.isoformat() if self.last_check else None,
            "metrics": self.metrics,
            "error": self.error,
        }


class SensorQuality:
    """Track packet capture sensor quality metrics."""

    def __init__(self):
        self.packets_received: int = 0
        self.packets_dropped: int = 0
        self.events_processed: int = 0
        self.parser_errors: int = 0
        self._start_time: float = time.time()
        self._last_event_time: Optional[float] = None

    @property
    def drop_percentage(self) -> float:
        total = self.packets_received + self.packets_dropped
        if total == 0:
            return 0.0
        return round((self.packets_dropped / total) * 100, 2)

    @property
    def event_lag_seconds(self) -> float:
        if self._last_event_time is None:
            return 0.0
        return round(time.time() - self._last_event_time, 2)

    @property
    def uptime_seconds(self) -> float:
        return round(time.time() - self._start_time, 1)

    def record_packet(self, dropped: bool = False) -> None:
        if dropped:
            self.packets_dropped += 1
        else:
            self.packets_received += 1
            self._last_event_time = time.time()

    def record_event(self) -> None:
        self.events_processed += 1
        self._last_event_time = time.time()

    def record_error(self) -> None:
        self.parser_errors += 1

    def to_dict(self) -> dict[str, Any]:
        return {
            "packets_received": self.packets_received,
            "packets_dropped": self.packets_dropped,
            "drop_percentage": self.drop_percentage,
            "events_processed": self.events_processed,
            "parser_errors": self.parser_errors,
            "event_lag_seconds": self.event_lag_seconds,
            "uptime_seconds": self.uptime_seconds,
        }


class HealthMonitor:
    """Monitors all Netra platform components."""

    def __init__(self):
        self.components: dict[str, ComponentHealth] = {
            "database": ComponentHealth("database"),
            "valkey": ComponentHealth("valkey"),
            "capture_engine": ComponentHealth("capture_engine"),
            "zeek": ComponentHealth("zeek"),
            "suricata": ComponentHealth("suricata"),
            "ml_inference": ComponentHealth("ml_inference"),
            "websocket": ComponentHealth("websocket"),
            "frontend": ComponentHealth("frontend"),
        }
        self.sensor_quality = SensorQuality()
        self._start_time = datetime.now(timezone.utc)

    def update_component(self, name: str, status: str,
                         metrics: Optional[dict] = None,
                         error: Optional[str] = None) -> None:
        if name not in self.components:
            self.components[name] = ComponentHealth(name)
        comp = self.components[name]
        if status == "healthy":
            comp.set_healthy(metrics)
        elif status == "degraded":
            comp.set_degraded(error or "degraded", metrics)
        elif status == "down":
            comp.set_down(error or "component down")
        else:
            comp.status = status
            comp.last_check = datetime.now(timezone.utc)

    def get_system_health(self) -> dict[str, Any]:
        component_list = [c.to_dict() for c in self.components.values()]
        statuses = [c.status for c in self.components.values()]
        if all(s == "healthy" for s in statuses):
            overall = "healthy"
        elif any(s == "down" for s in statuses):
            overall = "degraded"
        elif any(s == "degraded" for s in statuses):
            overall = "degraded"
        else:
            overall = "unknown"

        system_metrics = self._get_system_metrics()

        return {
            "overall_status": overall,
            "components": component_list,
            "sensor_quality": self.sensor_quality.to_dict(),
            "system_metrics": system_metrics,
            "uptime": str(datetime.now(timezone.utc) - self._start_time),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def get_sensor_metrics(self) -> dict[str, Any]:
        return {
            "sensor_quality": self.sensor_quality.to_dict(),
            "capture_status": self.components.get("capture_engine", ComponentHealth("capture_engine")).to_dict(),
            "zeek_status": self.components.get("zeek", ComponentHealth("zeek")).to_dict(),
            "suricata_status": self.components.get("suricata", ComponentHealth("suricata")).to_dict(),
        }

    @staticmethod
    def _get_system_metrics() -> dict[str, Any]:
        try:
            import psutil
            cpu_percent = psutil.cpu_percent(interval=0.1)
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage("/") if platform.system() != "Windows" else psutil.disk_usage("C:\\")
            return {
                "cpu_percent": cpu_percent,
                "memory_percent": mem.percent,
                "memory_used_gb": round(mem.used / (1024**3), 2),
                "memory_total_gb": round(mem.total / (1024**3), 2),
                "disk_percent": disk.percent,
                "disk_used_gb": round(disk.used / (1024**3), 2),
                "disk_total_gb": round(disk.total / (1024**3), 2),
            }
        except ImportError:
            return {
                "cpu_percent": 0.0,
                "memory_percent": 0.0,
                "disk_percent": 0.0,
                "note": "psutil not installed",
            }
