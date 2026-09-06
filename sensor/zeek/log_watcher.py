import os
import json
import time
import logging
import threading
from pathlib import Path
from typing import Callable, Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class ZeekLogWatcher:
    def __init__(self, log_dir: str):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.callbacks: List[Callable[[Dict[str, Any]], None]] = []
        self.is_running = False
        self._thread = None
        
        self.tracked_files = {
            "conn.log": 0,
            "dns.log": 0,
            "http.log": 0,
            "ssl.log": 0,
            "ssh.log": 0,
            "dhcp.log": 0,
            "files.log": 0,
            "notice.log": 0,
            "weird.log": 0
        }
        
        self._headers: Dict[str, List[str]] = {}

    def add_callback(self, callback: Callable[[Dict[str, Any]], None]):
        self.callbacks.append(callback)

    def _parse_line(self, log_type: str, line: str) -> Optional[Dict[str, Any]]:
        if line.lstrip().startswith("{"):
            try:
                data = json.loads(line)
                data.update(log_type=log_type.replace(".log", ""), source="zeek")
                return data
            except (ValueError, AttributeError):
                return None
        if line.startswith("#"):
            if line.startswith("#fields"):
                self._headers[log_type] = line.strip().split("\t")[1:]
            return None
            
        if log_type not in self._headers:
            return None
            
        parts = line.strip().split("\t")
        if len(parts) != len(self._headers[log_type]):
            return None
            
        data = dict(zip(self._headers[log_type], parts))
        data["log_type"] = log_type.replace(".log", "")
        data["source"] = "zeek"
        return data

    def _watch_loop(self):
        logger.info(f"Starting Zeek log watcher in {self.log_dir}")
        while self.is_running:
            for log_file in self.tracked_files.keys():
                file_path = self.log_dir / log_file
                if not file_path.exists():
                    continue
                
                try:
                    if file_path.stat().st_size < self.tracked_files[log_file]:
                        self.tracked_files[log_file] = 0
                        self._headers.pop(log_file, None)
                    with open(file_path, "r") as f:
                        f.seek(self.tracked_files[log_file])
                        while True:
                            position = f.tell()
                            line = f.readline()
                            if not line:
                                break
                            if not line.endswith("\n"):
                                f.seek(position)
                                break
                            parsed = self._parse_line(log_file, line)
                            if parsed:
                                for cb in self.callbacks:
                                    try:
                                        cb(parsed)
                                    except Exception as e:
                                        logger.error(f"Callback error on {log_file}: {e}")
                        self.tracked_files[log_file] = f.tell()
                except Exception as e:
                    logger.error(f"Error reading {log_file}: {e}")
            
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
