import psutil
import time
import threading
import logging
from typing import Dict, Any, Callable

logger = logging.getLogger(__name__)

class SensorHealthReporter:
    def __init__(self, sensor_id: str, interval_seconds: int = 60):
        self.sensor_id = sensor_id
        self.interval_seconds = interval_seconds
        self.callbacks = []
        self.is_running = False
        self._thread = None
        self.components_status = {
            "pcap_capture": "unknown",
            "zeek": "unknown",
            "suricata": "unknown"
        }

    def add_callback(self, callback: Callable[[Dict[str, Any]], None]):
        self.callbacks.append(callback)

    def update_component_status(self, component: str, status: str):
        self.components_status[component] = status

    def _generate_report(self) -> Dict[str, Any]:
        return {
            "sensor_id": self.sensor_id,
            "timestamp": time.time(),
            "cpu_percent": psutil.cpu_percent(interval=None),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage_percent": psutil.disk_usage('/').percent,
            "components": self.components_status
        }

    def _report_loop(self):
        logger.info("Starting health reporter")
        while self.is_running:
            report = self._generate_report()
            for cb in self.callbacks:
                try:
                    cb(report)
                except Exception as e:
                    logger.error(f"Health callback error: {e}")
            time.sleep(self.interval_seconds)

    def start(self):
        if self.is_running: return
        self.is_running = True
        self._thread = threading.Thread(target=self._report_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self.is_running = False
        if self._thread:
            self._thread.join(timeout=2.0)
