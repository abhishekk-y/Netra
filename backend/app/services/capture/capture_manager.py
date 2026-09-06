"""
Netra — Capture Manager
Orchestrates packet capture from network interfaces and PCAP file imports.
"""
from __future__ import annotations

import os
import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


class CaptureSession:
    """Represents an active or completed capture session."""

    def __init__(self, interface: str, capture_dir: str):
        self.session_id = str(uuid.uuid4())
        self.interface = interface
        self.capture_dir = capture_dir
        self.status: str = "idle"
        self.started_at: Optional[datetime] = None
        self.stopped_at: Optional[datetime] = None
        self.packets_captured: int = 0
        self.bytes_captured: int = 0
        self.pcap_files: list[str] = []
        self.error: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "interface": self.interface,
            "status": self.status,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "stopped_at": self.stopped_at.isoformat() if self.stopped_at else None,
            "packets_captured": self.packets_captured,
            "bytes_captured": self.bytes_captured,
            "pcap_files_count": len(self.pcap_files),
            "error": self.error,
        }


class CaptureManager:
    """Manages packet capture sessions and PCAP file imports."""

    def __init__(self, base_dir: str = "evidence/pcap"):
        self.base_dir = Path(base_dir)
        self.continuous_dir = self.base_dir / "continuous"
        self.incident_dir = self.base_dir / "incident"
        self.imported_dir = self.base_dir / "imported"
        self._sessions: dict[str, CaptureSession] = {}
        self._active_session: Optional[str] = None
        self._ensure_dirs()

    def _ensure_dirs(self) -> None:
        for d in [self.continuous_dir, self.incident_dir, self.imported_dir]:
            d.mkdir(parents=True, exist_ok=True)

    def start_capture(self, interface: str = "any") -> CaptureSession:
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        capture_dir = str(self.continuous_dir / date_str)
        os.makedirs(capture_dir, exist_ok=True)
        session = CaptureSession(interface, capture_dir)
        session.status = "capturing"
        session.started_at = datetime.now(timezone.utc)
        self._sessions[session.session_id] = session
        self._active_session = session.session_id
        return session

    def stop_capture(self, session_id: Optional[str] = None) -> Optional[CaptureSession]:
        sid = session_id or self._active_session
        if not sid or sid not in self._sessions:
            return None
        session = self._sessions[sid]
        session.status = "stopped"
        session.stopped_at = datetime.now(timezone.utc)
        if self._active_session == sid:
            self._active_session = None
        return session

    def record_packet(self, session_id: Optional[str] = None, size: int = 0) -> None:
        sid = session_id or self._active_session
        if sid and sid in self._sessions:
            self._sessions[sid].packets_captured += 1
            self._sessions[sid].bytes_captured += size

    def register_pcap_file(self, filepath: str, session_id: Optional[str] = None) -> dict[str, str]:
        sid = session_id or self._active_session
        if sid and sid in self._sessions:
            self._sessions[sid].pcap_files.append(filepath)
        sha256 = self._hash_file(filepath)
        manifest = {
            "filepath": filepath,
            "sha256": sha256,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "session_id": sid or "imported",
            "size_bytes": os.path.getsize(filepath) if os.path.exists(filepath) else 0,
        }
        manifest_path = filepath + ".manifest.json"
        hash_path = filepath + ".sha256"
        try:
            with open(manifest_path, "w") as f:
                json.dump(manifest, f, indent=2)
            with open(hash_path, "w") as f:
                f.write(sha256)
        except OSError:
            pass
        return manifest

    def import_pcap(self, source_path: str, label: str = "") -> dict[str, Any]:
        if not os.path.exists(source_path):
            return {"error": "File not found", "path": source_path}
        import shutil
        filename = os.path.basename(source_path)
        dest = str(self.imported_dir / filename)
        shutil.copy2(source_path, dest)
        manifest = self.register_pcap_file(dest)
        manifest["label"] = label
        manifest["source"] = "import"
        return manifest

    def create_incident_capture(self, incident_id: str) -> str:
        inc_dir = self.incident_dir / incident_id
        inc_dir.mkdir(parents=True, exist_ok=True)
        chain = {
            "incident_id": incident_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "sensor": "netra",
            "integrity": "sha256",
            "files": [],
        }
        chain_path = str(inc_dir / "chain_of_custody.json")
        with open(chain_path, "w") as f:
            json.dump(chain, f, indent=2)
        return str(inc_dir)

    def get_session(self, session_id: str) -> Optional[dict]:
        session = self._sessions.get(session_id)
        return session.to_dict() if session else None

    def get_active_session(self) -> Optional[dict]:
        if self._active_session and self._active_session in self._sessions:
            return self._sessions[self._active_session].to_dict()
        return None

    def get_all_sessions(self) -> list[dict]:
        return [s.to_dict() for s in self._sessions.values()]

    @staticmethod
    def _hash_file(filepath: str) -> str:
        sha256 = hashlib.sha256()
        try:
            with open(filepath, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except (OSError, IOError):
            return "error_hashing"

    def get_stats(self) -> dict[str, Any]:
        total_pcaps = 0
        total_bytes = 0
        for session in self._sessions.values():
            total_pcaps += len(session.pcap_files)
            total_bytes += session.bytes_captured
        return {
            "total_sessions": len(self._sessions),
            "active_session": self._active_session is not None,
            "total_pcap_files": total_pcaps,
            "total_bytes_captured": total_bytes,
        }
