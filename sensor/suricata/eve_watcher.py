import json
import time
import logging
import threading
from pathlib import Path
from typing import Callable, Dict, Any, List

logger = logging.getLogger(__name__)

class SuricataEVEWatcher:
    def __init__(self, eve_path: str = "/var/log/suricata/eve.json"):
        self.eve_path = Path(eve_path)
        self.callbacks: List[Callable[[Dict[str, Any]], None]] = []
        self.is_running = False
        self._thread = None
        self._position = 0

    def add_callback(self, callback: Callable[[Dict[str, Any]], None]):
        self.callbacks.append(callback)

    def _watch_loop(self):
        logger.info(f"Starting Suricata EVE watcher on {self.eve_path}")
        while self.is_running:
            if not self.eve_path.exists():
                time.sleep(2)
                continue
                
            try:
                # Handle file rotation (size shrank)
                current_size = self.eve_path.stat().st_size
                if current_size < self._position:
                    self._position = 0
                    
                with open(self.eve_path, "r") as f:
                    f.seek(self._position)
                    while True:
                        position = f.tell()
                        line = f.readline()
                        if not line:
                            break
                        if not line.endswith("\n"):
                            f.seek(position)
                            break
                        try:
                            data = json.loads(line.strip())
                            data["source"] = "suricata"
                            for cb in self.callbacks:
                                try:
                                    cb(data)
                                except Exception as e:
                                    logger.error(f"Callback error on EVE event: {e}")
                        except json.JSONDecodeError:
                            continue
                    self._position = f.tell()
            except Exception as e:
                logger.error(f"Error reading EVE log: {e}")
            
            time.sleep(1)

    def start(self):
        if self.is_running:
            return
        self.is_running = True
        self._thread = threading.Thread(target=self._watch_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self.is_running = False
        if self._thread:
            self._thread.join(timeout=2.0)
