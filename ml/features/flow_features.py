import math
import numpy as np
from typing import Dict, Any, List, Optional

class FlowFeatureExtractor:
    """Extracts features from network flows."""
    
    def __init__(self):
        self.well_known_port_limit = 1024
        self.ephemeral_port_start = 49152

    def _safe_div(self, a: float, b: float, default: float = 0.0) -> float:
        if b == 0 or math.isnan(b):
            return default
        return a / b

    def _safe_entropy(self, values: List[int]) -> float:
        if not values:
            return 0.0
        counts = {}
        for v in values:
            counts[v] = counts.get(v, 0) + 1
        total = len(values)
        entropy = 0.0
        for count in counts.values():
            p = count / total
            if p > 0:
                entropy -= p * math.log2(p)
        return entropy

    def extract(self, flow: Dict[str, Any]) -> Dict[str, float]:
        """
        Extract flow features from a raw flow dictionary.
        Expected keys in flow: 
        duration_ms, fwd_packets, bwd_packets, fwd_bytes, bwd_bytes,
        fwd_pkt_lens (list), bwd_pkt_lens (list), fwd_iats (list), bwd_iats (list),
        syn_count, ack_count, fin_count, rst_count, psh_count, urg_count,
        retransmission_count, src_port, dst_port, protocol
        """
        f = {}
        
        # Duration features
        duration_ms = float(flow.get("duration_ms", 0.0))
        f["duration_ms"] = duration_ms
        f["is_long_flow"] = 1.0 if duration_ms > 60000 else 0.0
        
        # Packet features
        fwd_pkts = float(flow.get("fwd_packets", 0))
        bwd_pkts = float(flow.get("bwd_packets", 0))
        total_pkts = fwd_pkts + bwd_pkts
        f["total_packets"] = total_pkts
        f["fwd_packets"] = fwd_pkts
        f["bwd_packets"] = bwd_pkts
        f["packet_ratio"] = self._safe_div(fwd_pkts, total_pkts)
        
        fwd_pkt_lens = flow.get("fwd_pkt_lens", [])
        bwd_pkt_lens = flow.get("bwd_pkt_lens", [])
        all_pkt_lens = fwd_pkt_lens + bwd_pkt_lens
        
        f["fwd_pkt_len_mean"] = float(np.mean(fwd_pkt_lens)) if fwd_pkt_lens else 0.0
        f["fwd_pkt_len_std"] = float(np.std(fwd_pkt_lens)) if fwd_pkt_lens else 0.0
        f["fwd_pkt_len_min"] = float(np.min(fwd_pkt_lens)) if fwd_pkt_lens else 0.0
        f["fwd_pkt_len_max"] = float(np.max(fwd_pkt_lens)) if fwd_pkt_lens else 0.0
        
        f["bwd_pkt_len_mean"] = float(np.mean(bwd_pkt_lens)) if bwd_pkt_lens else 0.0
        f["bwd_pkt_len_std"] = float(np.std(bwd_pkt_lens)) if bwd_pkt_lens else 0.0
        f["bwd_pkt_len_min"] = float(np.min(bwd_pkt_lens)) if bwd_pkt_lens else 0.0
        f["bwd_pkt_len_max"] = float(np.max(bwd_pkt_lens)) if bwd_pkt_lens else 0.0
        
        # Byte features
        fwd_bytes = float(flow.get("fwd_bytes", sum(fwd_pkt_lens)))
        bwd_bytes = float(flow.get("bwd_bytes", sum(bwd_pkt_lens)))
        total_bytes = fwd_bytes + bwd_bytes
        f["total_bytes"] = total_bytes
        f["fwd_bytes"] = fwd_bytes
        f["bwd_bytes"] = bwd_bytes
        f["byte_ratio"] = self._safe_div(fwd_bytes, total_bytes)
        f["bytes_per_packet"] = self._safe_div(total_bytes, total_pkts)
        
        # Timing features
        fwd_iats = flow.get("fwd_iats", [])
        bwd_iats = flow.get("bwd_iats", [])
        all_iats = fwd_iats + bwd_iats
        
        f["fwd_iat_mean"] = float(np.mean(fwd_iats)) if fwd_iats else 0.0
        f["fwd_iat_std"] = float(np.std(fwd_iats)) if fwd_iats else 0.0
        f["fwd_iat_min"] = float(np.min(fwd_iats)) if fwd_iats else 0.0
        f["fwd_iat_max"] = float(np.max(fwd_iats)) if fwd_iats else 0.0
        
        f["bwd_iat_mean"] = float(np.mean(bwd_iats)) if bwd_iats else 0.0
        f["bwd_iat_std"] = float(np.std(bwd_iats)) if bwd_iats else 0.0
        f["bwd_iat_min"] = float(np.min(bwd_iats)) if bwd_iats else 0.0
        f["bwd_iat_max"] = float(np.max(bwd_iats)) if bwd_iats else 0.0
        
        f["flow_iat_mean"] = float(np.mean(all_iats)) if all_iats else 0.0
        f["flow_iat_std"] = float(np.std(all_iats)) if all_iats else 0.0
        
        # TCP features
        f["syn_count"] = float(flow.get("syn_count", 0))
        f["ack_count"] = float(flow.get("ack_count", 0))
        f["fin_count"] = float(flow.get("fin_count", 0))
        f["rst_count"] = float(flow.get("rst_count", 0))
        f["psh_count"] = float(flow.get("psh_count", 0))
        f["urg_count"] = float(flow.get("urg_count", 0))
        
        f["syn_flag_ratio"] = self._safe_div(f["syn_count"], total_pkts)
        f["fin_flag_ratio"] = self._safe_div(f["fin_count"], total_pkts)
        f["rst_flag_ratio"] = self._safe_div(f["rst_count"], total_pkts)
        f["retransmission_count"] = float(flow.get("retransmission_count", 0))
        
        # Flow features
        dur_sec = self._safe_div(duration_ms, 1000.0)
        f["packets_per_second"] = self._safe_div(total_pkts, dur_sec)
        f["bytes_per_second"] = self._safe_div(total_bytes, dur_sec)
        f["is_bidirectional"] = 1.0 if (fwd_pkts > 0 and bwd_pkts > 0) else 0.0
        
        # Port features
        src_port = float(flow.get("src_port", 0))
        dst_port = float(flow.get("dst_port", 0))
        f["src_port"] = src_port
        f["dst_port"] = dst_port
        f["is_well_known_port"] = 1.0 if dst_port < self.well_known_port_limit else 0.0
        f["is_ephemeral_port"] = 1.0 if dst_port >= self.ephemeral_port_start else 0.0
        
        if dst_port < self.well_known_port_limit:
            port_class = 0.0 # well_known
        elif dst_port >= self.ephemeral_port_start:
            port_class = 2.0 # ephemeral
        else:
            port_class = 1.0 # registered
        f["port_class"] = port_class
        
        # Protocol features
        proto = flow.get("protocol", 6)
        if isinstance(proto, str):
            proto = proto.lower()
            if proto == 'tcp': proto = 6
            elif proto == 'udp': proto = 17
            elif proto == 'icmp': proto = 1
            else: proto = 0
            
        f["protocol_encoded"] = float(proto)
        f["is_tcp"] = 1.0 if proto == 6 else 0.0
        f["is_udp"] = 1.0 if proto == 17 else 0.0
        f["is_icmp"] = 1.0 if proto == 1 else 0.0
        
        # Entropy features
        f["packet_length_entropy"] = self._safe_entropy(all_pkt_lens)
        f["payload_byte_entropy"] = self._safe_entropy(flow.get("payload_bytes", []))
        
        # Ensure all are float and replace inf/nan
        for k, v in f.items():
            if math.isnan(v) or math.isinf(v):
                f[k] = 0.0
                
        return f
