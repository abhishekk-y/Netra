import networkx as nx
import numpy as np
from typing import Dict, Any, List

class GraphFeatureExtractor:
    """Extracts topological and graph-based features using NetworkX."""
    
    def __init__(self):
        self.critical_assets = set()
        
    def set_critical_assets(self, assets: List[str]):
        self.critical_assets = set(assets)

    def extract(self, g: nx.DiGraph, node: str) -> Dict[str, float]:
        """
        Extract graph features for a specific node in a directed graph.
        The graph should have edge weights representing bytes or packets.
        """
        f = {}
        
        if node not in g:
            keys = ["in_degree", "out_degree", "weighted_in_degree", "weighted_out_degree",
                    "betweenness_centrality", "closeness_centrality", "pagerank", 
                    "clustering_coeff", "hub_score", "authority_score", "ego_graph_size",
                    "distance_to_critical", "connected_component_size", 
                    "unique_services_exposed", "neighbor_anomaly_score"]
            return {k: 0.0 for k in keys}
            
        f["in_degree"] = float(g.in_degree(node))
        f["out_degree"] = float(g.out_degree(node))
        
        f["weighted_in_degree"] = float(g.in_degree(node, weight='bytes'))
        f["weighted_out_degree"] = float(g.out_degree(node, weight='bytes'))
        
        # Centralities can be computationally expensive on large graphs, 
        # normally computed globally and cached. Calculating per-node ego approx here.
        ego = nx.ego_graph(g, node, radius=2)
        
        f["ego_graph_size"] = float(ego.number_of_nodes())
        
        try:
            f["clustering_coeff"] = float(nx.clustering(g, node))
        except:
            f["clustering_coeff"] = 0.0
            
        # For full graph metrics, they should be precomputed. 
        # Doing a local approximation if missing.
        f["betweenness_centrality"] = float(g.nodes[node].get('betweenness', 0.0))
        f["closeness_centrality"] = float(g.nodes[node].get('closeness', 0.0))
        f["pagerank"] = float(g.nodes[node].get('pagerank', 0.0))
        f["hub_score"] = float(g.nodes[node].get('hub', 0.0))
        f["authority_score"] = float(g.nodes[node].get('authority', 0.0))
        
        # Distance to critical assets
        min_dist = float('inf')
        for asset in self.critical_assets:
            if asset in g and nx.has_path(g, node, asset):
                dist = nx.shortest_path_length(g, node, asset)
                if dist < min_dist:
                    min_dist = dist
        f["distance_to_critical"] = float(min_dist) if min_dist != float('inf') else -1.0
        
        # Connected component (weakly connected for DiGraph)
        try:
            wcc = nx.node_connected_component(g.to_undirected(), node)
            f["connected_component_size"] = float(len(wcc))
        except:
            f["connected_component_size"] = 1.0
            
        f["unique_services_exposed"] = float(g.nodes[node].get('unique_services', 0))
        
        # Neighbor anomaly (avg anomaly of neighbors)
        neighbors = list(g.successors(node)) + list(g.predecessors(node))
        anomaly_scores = [g.nodes[n].get('anomaly_score', 0.0) for n in neighbors if n in g]
        f["neighbor_anomaly_score"] = float(np.mean(anomaly_scores)) if anomaly_scores else 0.0
        
        for k, v in f.items():
            if np.isnan(v) or np.isinf(v):
                f[k] = 0.0
                
        return f
