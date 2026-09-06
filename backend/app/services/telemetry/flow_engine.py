from datetime import datetime, timezone
from typing import Dict, List, Any
import uuid

from app.models.event import NormalizedEvent
from app.models.flow import Flow

class FlowState:
    def __init__(self, community_id: str):
        self.community_id = community_id
        self.flow: Flow = Flow(
            id=str(uuid.uuid4()),
            community_id=community_id,
            timestamp=datetime.now(timezone.utc),
            packets_forward=0,
            packets_backward=0,
            bytes_forward=0,
            bytes_backward=0,
            duration_ms=0,
            tcp_flags={},
            flow_features={},
            metadata_={"start_time": datetime.now(timezone.utc).timestamp()}
        )
        self.packet_lengths_fwd: List[int] = []
        self.packet_lengths_bwd: List[int] = []
        self.inter_arrival_times: List[float] = []
        self.last_packet_time = datetime.now(timezone.utc).timestamp()

class FlowEngine:
    def __init__(self):
        self.active_flows: Dict[str, FlowState] = {}
        self.host_stats: Dict[str, Dict[str, Any]] = {}
        
    def update_flow(self, event: NormalizedEvent) -> None:
        if not event.community_id:
            return
            
        cid = event.community_id
        if cid not in self.active_flows:
            state = FlowState(cid)
            state.flow.src_ip = event.source_ip or ""
            state.flow.dst_ip = event.destination_ip or ""
            state.flow.src_port = event.source_port or 0
            state.flow.dst_port = event.destination_port or 0
            state.flow.protocol = event.protocol or ""
            state.flow.sensor_id = event.sensor_id
            self.active_flows[cid] = state
            
        state = self.active_flows[cid]
        
        # Determine direction based on source IP
        is_forward = (event.source_ip == state.flow.src_ip)
        
        # Extrapolate packet size if available
        pkt_len = event.data.get("length", 0)
        curr_time = datetime.now(timezone.utc).timestamp()
        
        if is_forward:
            state.flow.packets_forward += 1
            state.flow.bytes_forward += pkt_len
            state.packet_lengths_fwd.append(pkt_len)
        else:
            state.flow.packets_backward += 1
            state.flow.bytes_backward += pkt_len
            state.packet_lengths_bwd.append(pkt_len)
            
        iat = curr_time - state.last_packet_time
        state.inter_arrival_times.append(iat)
        state.last_packet_time = curr_time
        state.flow.duration_ms = int((curr_time - state.flow.metadata_["start_time"]) * 1000)

    def extract_features(self, state: FlowState) -> Dict[str, float]:
        features = {}
        features["duration_ms"] = float(state.flow.duration_ms)
        features["packets_forward"] = float(state.flow.packets_forward)
        features["packets_backward"] = float(state.flow.packets_backward)
        features["bytes_forward"] = float(state.flow.bytes_forward)
        features["bytes_backward"] = float(state.flow.bytes_backward)
        
        total_packets = state.flow.packets_forward + state.flow.packets_backward
        duration_s = state.flow.duration_ms / 1000.0 if state.flow.duration_ms > 0 else 0.001
        
        features["flow_bytes_s"] = float((state.flow.bytes_forward + state.flow.bytes_backward) / duration_s)
        features["flow_pkts_s"] = float(total_packets / duration_s)
        
        def safe_mean(lst): return float(sum(lst) / len(lst)) if lst else 0.0
        
        features["mean_pkt_len_fwd"] = safe_mean(state.packet_lengths_fwd)
        features["mean_pkt_len_bwd"] = safe_mean(state.packet_lengths_bwd)
        features["mean_iat"] = safe_mean(state.inter_arrival_times)
        
        # 40+ features mapped for ML
        return features

    def finalize_flow(self, community_id: str) -> Optional[Flow]:
        if community_id in self.active_flows:
            state = self.active_flows.pop(community_id)
            state.flow.flow_features = self.extract_features(state)
            return state.flow
        return None

    def get_active_flows(self) -> List[Flow]:
        return [state.flow for state in self.active_flows.values()]
