import uuid
from typing import Dict, Any, List
from datetime import datetime, timezone

from app.models.flow import Flow
from app.models.alert import Alert
from app.services.detection.statistical_engine import StatisticalAnomalyEngine
from app.services.detection.ml_engine import MLDetectionEngine
from app.services.detection.correlation_engine import CorrelationEngine
from app.core.events import event_bus

class DetectionResult:
    def __init__(self):
        self.is_alert: bool = False
        self.score: float = 0.0
        self.attack_type: str = "Unknown"
        self.evidence: Dict[str, Any] = {}

class DetectionManager:
    def __init__(self):
        self.statistical_engine = StatisticalAnomalyEngine()
        self.ml_engine = MLDetectionEngine()
        self.correlation_engine = CorrelationEngine()
        
    async def process_flow(self, flow: Flow) -> DetectionResult:
        result = DetectionResult()
        
        # 1. Statistical Anomaly
        # Simplify flow features to flat float dict
        feat_dict = {}
        for k, v in flow.flow_features.items():
            if isinstance(v, (int, float)):
                feat_dict[k] = float(v)
                
        # Basic check for single flow (normally stat engine checks across time windows)
        stat_anomaly = self.statistical_engine.z_score_anomaly(feat_dict.get("flow_bytes_s", 0), 1000.0, 500.0)
        
        # 2. ML Classification & Anomaly
        ml_class, ml_conf, ml_probs = self.ml_engine.classify_flow(feat_dict)
        ml_anomaly = self.ml_engine.anomaly_score(feat_dict)
        
        # 3. Signature (Simulated from events or Suricata rules attached to flow)
        sig_score = 0.0
        if "suricata_alert" in flow.metadata_:
            sig_score = 80.0
            
        # Fusion
        fused_score = max(stat_anomaly * 0.4, ml_anomaly * 0.8, sig_score, ml_conf * 100 if ml_class != "Benign" else 0)
        
        result.score = fused_score
        if fused_score > 60.0:
            result.is_alert = True
            result.attack_type = ml_class if ml_class != "Benign" else "Anomalous Traffic"
            result.evidence = {
                "stat_anomaly": stat_anomaly,
                "ml_anomaly": ml_anomaly,
                "ml_classification": ml_class,
                "ml_confidence": ml_conf,
                "flow_id": flow.id
            }
            
            # Create Alert
            alert = Alert(
                id=str(uuid.uuid4()),
                timestamp=datetime.now(timezone.utc),
                rule_id=f"ML-{result.attack_type}",
                name=f"Detected {result.attack_type}",
                description=f"Detection engine identified malicious behavior with score {fused_score:.1f}",
                severity="high" if fused_score > 80 else "medium",
                category=result.attack_type,
                src_ip=flow.src_ip,
                dst_ip=flow.dst_ip,
                community_id=flow.community_id,
                score=fused_score,
                confidence=ml_conf,
                evidence=result.evidence
            )
            
            # Send to correlator
            self.correlation_engine.add_alert(alert)
            
            # Emit event
            await event_bus.publish("alerts", alert)
            
        return result
