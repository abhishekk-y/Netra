from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class TopologyNode(BaseModel):
    id: str
    type: str
    label: str
    properties: Dict[str, Any] = {}
    layer: Optional[str] = None
    zone: Optional[str] = None

class TopologyEdge(BaseModel):
    id: str
    source_id: str
    target_id: str
    type: str
    first_seen: datetime
    last_seen: datetime
    metrics: Dict[str, Any] = {}

class TopologyGraph(BaseModel):
    nodes: List[TopologyNode] = []
    edges: List[TopologyEdge] = []

class TopologyDiff(BaseModel):
    added_nodes: List[TopologyNode] = []
    removed_nodes: List[TopologyNode] = []
    added_edges: List[TopologyEdge] = []
    removed_edges: List[TopologyEdge] = []
    changed_edges: List[Dict[str, Any]] = []

class PathAnalysis(BaseModel):
    source_id: str
    target_id: str
    path: List[str]  # List of node IDs
    services: List[str] = []
    latency_ms: Optional[float] = None
    risk_score: float = 0.0
