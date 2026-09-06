from datetime import datetime, timezone
from typing import Dict, Any, Optional
import uuid
from app.models.topology import TopologySnapshot
from app.schemas.topology import TopologyDiff, TopologyNode, TopologyEdge

class SnapshotManager:
    def __init__(self):
        self.snapshots: Dict[str, TopologySnapshot] = {}
        
    def take_snapshot(self, graph: Dict[str, Any], trigger: str = 'periodic') -> TopologySnapshot:
        snap_id = str(uuid.uuid4())
        snapshot = TopologySnapshot(
            id=snap_id,
            timestamp=datetime.now(timezone.utc),
            nodes=graph.get("nodes", []),
            edges=graph.get("edges", []),
            is_incident_trigger=(trigger == 'incident')
        )
        self.snapshots[snap_id] = snapshot
        return snapshot
        
    def get_snapshot_at(self, target_time: datetime) -> Optional[TopologySnapshot]:
        if not self.snapshots:
            return None
        # Return closest snapshot
        closest = None
        min_diff = float('inf')
        for s in self.snapshots.values():
            diff = abs((s.timestamp - target_time).total_seconds())
            if diff < min_diff:
                min_diff = diff
                closest = s
        return closest
        
    def diff_snapshots(self, snap1: TopologySnapshot, snap2: TopologySnapshot) -> TopologyDiff:
        nodes1 = {n['id']: n for n in snap1.nodes}
        nodes2 = {n['id']: n for n in snap2.nodes}
        
        edges1 = {e['id']: e for e in snap1.edges}
        edges2 = {e['id']: e for e in snap2.edges}
        
        added_n = [TopologyNode(**nodes2[nid]) for nid in set(nodes2.keys()) - set(nodes1.keys())]
        removed_n = [TopologyNode(**nodes1[nid]) for nid in set(nodes1.keys()) - set(nodes2.keys())]
        
        added_e = [TopologyEdge(**edges2[eid]) for eid in set(edges2.keys()) - set(edges1.keys())]
        removed_e = [TopologyEdge(**edges1[eid]) for eid in set(edges1.keys()) - set(edges2.keys())]
        
        changed_e = [] # Implement property diff if needed
        
        return TopologyDiff(
            added_nodes=added_n,
            removed_nodes=removed_n,
            added_edges=added_e,
            removed_edges=removed_e,
            changed_edges=changed_e
        )
