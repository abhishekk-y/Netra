from typing import List, Dict, Any
from datetime import datetime, timezone
import uuid

from app.models.topology import TopologyNode, TopologyEdge

class TopologyBuilder:
    def build_graph(self, hosts: List[Dict[str, Any]], flows: List[Dict[str, Any]]) -> Dict[str, Any]:
        nodes = []
        edges = []
        
        for h in hosts:
            nodes.append(
                TopologyNode(
                    id=h.get("ip", str(uuid.uuid4())),
                    type=h.get("device_type", "Endpoint"),
                    label=h.get("hostname", h.get("ip", "Unknown")),
                    properties=h
                )
            )
            
        for f in flows:
            edges.append(
                TopologyEdge(
                    id=f.get("flow_id", str(uuid.uuid4())),
                    source_id=f.get("src_ip"),
                    target_id=f.get("dst_ip"),
                    type="logical_flow",
                    metrics={"bytes": f.get("bytes_forward", 0) + f.get("bytes_backward", 0)}
                )
            )
            
        self.assign_layers(nodes)
        
        return {
            "nodes": [n.__dict__ for n in nodes if not n.id.startswith('_')],
            "edges": [e.__dict__ for e in edges if not e.id.startswith('_')]
        }
        
    def assign_layers(self, nodes: List[TopologyNode]) -> None:
        for node in nodes:
            dtype = node.type.lower()
            if dtype in ["router", "firewall"]:
                node.layer = "core"
            elif dtype == "switch":
                node.layer = "distribution"
            elif dtype in ["server", "workstation", "iot"]:
                node.layer = "endpoint"
            else:
                node.layer = "access"
                
    def get_view(self, graph: Dict[str, Any], view_mode: str) -> Dict[str, Any]:
        # Filter logic based on view_mode ('physical', 'logical', 'security')
        return graph # Return full graph for now
        
    def to_cytoscape_format(self, graph: Dict[str, Any]) -> List[Dict[str, Any]]:
        elements = []
        for n in graph.get("nodes", []):
            elements.append({"data": {"id": n["id"], "label": n["label"], "type": n["type"]}})
        for e in graph.get("edges", []):
            elements.append({"data": {"id": e["id"], "source": e["source_id"], "target": e["target_id"]}})
        return elements
