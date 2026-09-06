import math
import numpy as np
from collections import Counter
from typing import Dict, Any, List

class HostFeatureExtractor:
    """Extracts per-host behavioral features over time windows."""
    
    def __init__(self, time_window_sec: float = 60.0):
        self.time_window_sec = time_window_sec
        self.well_known_port_limit = 1024

    def _safe_div(self, a: float, b: float, default: float = 0.0) -> float:
        if b == 0 or math.isnan(b):
            return default
        return a / b

    def _safe_entropy(self, counts: List[int]) -> float:
        total = sum(counts)
        if total == 0: return 0.0
        entropy = 0.0
        for count in counts:
            p = count / total
            if p > 0:
                entropy -= p * math.log2(p)
        return entropy
        
    def _autocorrelation(self, times: List[float], lag: float = 1.0) -> float:
        if len(times) < 3: return 0.0
        # Simplistic periodicity score: bin timings and compute autocorrelation
        bins = min(1024, int(max(times) - min(times)))
        if bins < 3: return 0.0
        hist, _ = np.histogram(times, bins=bins)
        if np.std(hist) == 0: return 0.0
        autocorr = np.corrcoef(hist[:-1], hist[1:])[0, 1]
        return float(autocorr) if not math.isnan(autocorr) else 0.0

    def extract(self, host_ip: str, flows: List[Dict[str, Any]], baseline_peers: set = None) -> Dict[str, float]:
        """
        Extract behavioral features for a specific host over a window of flows.
        """
        baseline_peers = baseline_peers or set()
        flows = [flow for flow in flows if host_ip in (flow.get('src_ip'), flow.get('dst_ip'))]
        f = {}
        
        if not flows:
            # Return zeros for empty window
            keys = ["connections_per_second", "unique_peers", "unique_destinations", 
                    "unique_dst_ports", "unique_src_ports", "failed_connections", 
                    "dns_query_rate", "total_bytes_sent", "total_bytes_received", 
                    "byte_ratio", "avg_flow_duration", "connection_entropy", 
                    "fan_out", "fan_in", "new_peer_count", "rare_port_count", 
                    "rare_service_count", "periodicity_score", "avg_packet_size", 
                    "protocol_diversity", "is_scanning"]
            return {k: 0.0 for k in keys}

        peers = set()
        destinations = set()
        sources = set()
        dst_ports = set()
        src_ports = set()
        protocols = set()
        
        total_bytes_sent = 0
        total_bytes_received = 0
        total_packets = 0
        total_duration = 0
        rst_count = 0
        dns_queries = 0
        
        start_time = min(flow.get('timestamp', 0) for flow in flows)
        end_time = max(flow.get('timestamp', 0) for flow in flows)
        actual_window = max(end_time - start_time, 1.0) # at least 1s
        
        dst_counter = Counter()
        timings = []

        for flow in flows:
            src = flow.get('src_ip')
            dst = flow.get('dst_ip')
            sport = flow.get('src_port')
            dport = flow.get('dst_port')
            proto = flow.get('protocol')
            
            protocols.add(proto)
            timings.append(flow.get('timestamp', 0))
            
            if src == host_ip:
                destinations.add(dst)
                peers.add(dst)
                if dport is not None: dst_ports.add(dport)
                if sport is not None: src_ports.add(sport)
                total_bytes_sent += flow.get('fwd_bytes', 0)
                total_bytes_received += flow.get('bwd_bytes', 0)
                dst_counter[dst] += 1
                if dport == 53: dns_queries += 1
            elif dst == host_ip:
                sources.add(src)
                peers.add(src)
                if sport is not None: src_ports.add(sport)
                total_bytes_sent += flow.get('bwd_bytes', 0)
                total_bytes_received += flow.get('fwd_bytes', 0)
                
            rst_count += flow.get('rst_count', 0)
            total_packets += flow.get('total_packets', flow.get('fwd_packets', 0) + flow.get('bwd_packets', 0))
            total_duration += flow.get('duration_ms', 0)

        f["connections_per_second"] = len(flows) / actual_window
        f["unique_peers"] = float(len(peers))
        f["unique_destinations"] = float(len(destinations))
        f["unique_dst_ports"] = float(len(dst_ports))
        f["unique_src_ports"] = float(len(src_ports))
        f["failed_connections"] = self._safe_div(rst_count, len(flows))
        f["dns_query_rate"] = dns_queries / actual_window
        f["total_bytes_sent"] = float(total_bytes_sent)
        f["total_bytes_received"] = float(total_bytes_received)
        f["byte_ratio"] = self._safe_div(total_bytes_sent, total_bytes_sent + total_bytes_received)
        f["avg_flow_duration"] = self._safe_div(total_duration, len(flows))
        f["connection_entropy"] = self._safe_entropy(list(dst_counter.values()))
        f["fan_out"] = float(len(destinations))
        f["fan_in"] = float(len(sources))
        
        new_peers = peers - baseline_peers
        f["new_peer_count"] = float(len(new_peers))
        
        # Rare port logic
        f["rare_port_count"] = float(sum(1 for p in dst_ports if p > self.well_known_port_limit and p < 49152))
        f["rare_service_count"] = float(sum(1 for p in dst_ports if p not in {80, 443, 22, 53, 3389}))
        
        f["periodicity_score"] = self._autocorrelation(timings)
        f["avg_packet_size"] = self._safe_div(total_bytes_sent + total_bytes_received, total_packets)
        f["protocol_diversity"] = float(len(protocols))
        
        # Scanning heuristic: high fan-out, low bytes per connection
        is_scanning = 1.0 if (f["fan_out"] > 20 and f["byte_ratio"] > 0.8 and f["avg_packet_size"] < 100) else 0.0
        f["is_scanning"] = is_scanning
        
        # Clean up nans
        for k, v in f.items():
            if math.isnan(v) or math.isinf(v):
                f[k] = 0.0
                
        return f
