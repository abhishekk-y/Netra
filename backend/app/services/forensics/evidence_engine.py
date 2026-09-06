"""
Netra — Evidence Engine
Manages forensic evidence chains, integrity verification, and evidence graphs.
"""
from __future__ import annotations

import hashlib
import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


class EvidenceItem:
    """A single piece of forensic evidence."""

    __slots__ = (
        "evidence_id", "evidence_type", "source_type", "filepath",
        "sha256", "size_bytes", "created_at", "incident_id",
        "community_id", "flow_id", "metadata", "verified",
    )

    def __init__(self, evidence_type: str, source_type: str, filepath: str = ""):
        self.evidence_id = str(uuid.uuid4())
        self.evidence_type = evidence_type
        self.source_type = source_type
        self.filepath = filepath
        self.sha256: str = ""
        self.size_bytes: int = 0
        self.created_at = datetime.now(timezone.utc)
        self.incident_id: Optional[str] = None
        self.community_id: Optional[str] = None
        self.flow_id: Optional[str] = None
        self.metadata: dict[str, Any] = {}
        self.verified: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "evidence_type": self.evidence_type,
            "source_type": self.source_type,
            "filepath": self.filepath,
            "sha256": self.sha256,
            "size_bytes": self.size_bytes,
            "created_at": self.created_at.isoformat(),
            "incident_id": self.incident_id,
            "community_id": self.community_id,
            "flow_id": self.flow_id,
            "verified": self.verified,
        }


class EvidenceChain:
    """Chain of custody for an incident's evidence."""

    def __init__(self, incident_id: str):
        self.incident_id = incident_id
        self.chain_id = str(uuid.uuid4())
        self.created_at = datetime.now(timezone.utc)
        self.items: list[EvidenceItem] = []
        self.events: list[dict[str, Any]] = []

    def add_item(self, item: EvidenceItem) -> None:
        item.incident_id = self.incident_id
        self.items.append(item)
        self.events.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": "evidence_added",
            "evidence_id": item.evidence_id,
            "type": item.evidence_type,
        })

    def to_dict(self) -> dict[str, Any]:
        return {
            "chain_id": self.chain_id,
            "incident_id": self.incident_id,
            "created_at": self.created_at.isoformat(),
            "items_count": len(self.items),
            "items": [i.to_dict() for i in self.items],
            "custody_events": self.events,
        }


class EvidenceEngine:
    """Manages forensic evidence, integrity, and evidence graph construction."""

    def __init__(self, evidence_dir: str = "evidence"):
        self.evidence_dir = Path(evidence_dir)
        self._chains: dict[str, EvidenceChain] = {}
        self._items: dict[str, EvidenceItem] = {}

    def create_chain(self, incident_id: str) -> EvidenceChain:
        chain = EvidenceChain(incident_id)
        self._chains[incident_id] = chain
        return chain

    def add_evidence(
        self,
        incident_id: str,
        evidence_type: str,
        source_type: str,
        filepath: str = "",
        community_id: Optional[str] = None,
        flow_id: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> EvidenceItem:
        if incident_id not in self._chains:
            self.create_chain(incident_id)
        chain = self._chains[incident_id]
        item = EvidenceItem(evidence_type, source_type, filepath)
        item.community_id = community_id
        item.flow_id = flow_id
        item.metadata = metadata or {}
        if filepath and os.path.exists(filepath):
            item.sha256 = self._hash_file(filepath)
            item.size_bytes = os.path.getsize(filepath)
            item.verified = True
        chain.add_item(item)
        self._items[item.evidence_id] = item
        return item

    def verify_integrity(self, evidence_id: str) -> dict[str, Any]:
        item = self._items.get(evidence_id)
        if not item:
            return {"verified": False, "error": "Evidence not found"}
        if not item.filepath or not os.path.exists(item.filepath):
            return {"verified": False, "error": "File not found"}
        current_hash = self._hash_file(item.filepath)
        matches = current_hash == item.sha256
        item.verified = matches
        return {
            "evidence_id": evidence_id,
            "verified": matches,
            "original_sha256": item.sha256,
            "current_sha256": current_hash,
            "file_exists": True,
        }

    def build_evidence_graph(self, incident_id: str) -> dict[str, Any]:
        chain = self._chains.get(incident_id)
        if not chain:
            return {"nodes": [], "edges": []}
        nodes: list[dict] = []
        edges: list[dict] = []
        incident_node = {"id": incident_id, "type": "incident", "label": f"Incident {incident_id[:8]}"}
        nodes.append(incident_node)
        flow_ids: set[str] = set()
        for item in chain.items:
            item_node = {
                "id": item.evidence_id,
                "type": item.evidence_type,
                "label": f"{item.evidence_type} ({item.source_type})",
                "verified": item.verified,
            }
            nodes.append(item_node)
            edges.append({"source": incident_id, "target": item.evidence_id, "relationship": "contains_evidence"})
            if item.flow_id and item.flow_id not in flow_ids:
                flow_ids.add(item.flow_id)
                flow_node = {"id": item.flow_id, "type": "flow", "label": f"Flow {item.flow_id[:8]}"}
                nodes.append(flow_node)
                edges.append({"source": item.evidence_id, "target": item.flow_id, "relationship": "derived_from"})
            if item.community_id:
                cid_node_id = f"cid_{item.community_id}"
                existing = any(n["id"] == cid_node_id for n in nodes)
                if not existing:
                    nodes.append({"id": cid_node_id, "type": "community_id", "label": item.community_id[:16]})
                edges.append({"source": item.evidence_id, "target": cid_node_id, "relationship": "correlates_via"})
        return {"incident_id": incident_id, "nodes": nodes, "edges": edges}

    def get_chain(self, incident_id: str) -> Optional[dict]:
        chain = self._chains.get(incident_id)
        return chain.to_dict() if chain else None

    def get_evidence(self, evidence_id: str) -> Optional[dict]:
        item = self._items.get(evidence_id)
        return item.to_dict() if item else None

    def export_chain(self, incident_id: str) -> Optional[str]:
        chain = self._chains.get(incident_id)
        if not chain:
            return None
        export_dir = self.evidence_dir / "exports" / incident_id
        export_dir.mkdir(parents=True, exist_ok=True)
        export_path = str(export_dir / "evidence_chain.json")
        with open(export_path, "w") as f:
            json.dump(chain.to_dict(), f, indent=2, default=str)
        return export_path

    @staticmethod
    def _hash_file(filepath: str) -> str:
        sha256 = hashlib.sha256()
        try:
            with open(filepath, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except (OSError, IOError):
            return "error"

    def get_stats(self) -> dict[str, int]:
        return {
            "total_chains": len(self._chains),
            "total_evidence_items": len(self._items),
        }
