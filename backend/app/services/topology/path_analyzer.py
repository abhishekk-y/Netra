import networkx as nx
from typing import Dict, Any, List
from app.schemas.topology import PathAnalysis

class PathAnalyzer:
    def __init__(self):
        self.graph = nx.DiGraph()
        
    def update_graph(self, topology_graph: Dict[str, Any]) -> None:
        self.graph.clear()
        for node in topology_graph.get("nodes", []):
            self.graph.add_node(node["id"], **node)
        for edge in topology_graph.get("edges", []):
            self.graph.add_edge(edge["source_id"], edge["target_id"], **edge)
            
    def find_path(self, src_ip: str, dst_ip: str) -> PathAnalysis:
        if src_ip not in self.graph or dst_ip not in self.graph:
            return PathAnalysis(source_id=src_ip, target_id=dst_ip, path=[])
            
        try:
            path = nx.shortest_path(self.graph, source=src_ip, target=dst_ip)
            
            services = []
            latency = 0.0
            
            # Simple aggregation along path
            for i in range(len(path) - 1):
                edge_data = self.graph.get_edge_data(path[i], path[i+1])
                if edge_data and "metrics" in edge_data:
                    latency += edge_data["metrics"].get("latency", 0.0)
                    if "service" in edge_data:
                        services.append(edge_data["service"])
                        
            return PathAnalysis(
                source_id=src_ip,
                target_id=dst_ip,
                path=path,
                services=list(set(services)),
                latency_ms=latency if latency > 0 else None,
                risk_score=0.0
            )
        except nx.NetworkXNoPath:
            return PathAnalysis(source_id=src_ip, target_id=dst_ip, path=[])
