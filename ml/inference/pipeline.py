"""Feature extraction and schema-aware inference using independently loaded models."""
from ml.features.flow_features import FlowFeatureExtractor
from ml.inference.engine import InferenceEngine


class InferencePipeline:
    def __init__(self, engine: InferenceEngine):
        self.engine = engine
        self.flow_extractor = FlowFeatureExtractor()

    def process_single_event(self, raw_flow):
        features = self.flow_extractor.extract(raw_flow)
        results = self.engine.infer_flow(features)
        return {"flow_id": raw_flow.get("flow_id", "unknown"),
                "attack_type": results.get("attack_type", "UNKNOWN"),
                "confidence": results.get("confidence"),
                "anomaly_score": results.get("anomaly_score"),
                "model_status": results["model_status"],
                "model_errors": results["errors"],
                "extracted_features_count": len(features)}

    def process_batch(self, raw_flows):
        return [self.process_single_event(flow) for flow in raw_flows]
