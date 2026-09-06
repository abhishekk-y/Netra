"""Optional trained-artifact inference with an explicit unavailable state."""
from collections import deque
from functools import wraps
import importlib
import time
import numpy as np


class InferenceEngine:
    LOADERS = {
        "classifier": ("ml.models.classifier", "FlowClassifier", False),
        "anomaly": ("ml.models.anomaly", "AnomalyDetector", False),
        "autoencoder": ("ml.models.autoencoder", "BehaviorAutoencoder", True),
        "sequence": ("ml.models.sequence_model", "SequenceForecaster", True),
        "temporal": ("ml.models.temporal_model", "TemporalForecaster", True),
        "target": ("ml.models.target_model", "TargetPredictor", True),
    }

    def __init__(self, model_paths=None):
        self.models, self.load_errors = {}, {}
        self.latency_stats = deque(maxlen=1000)
        for name, path in (model_paths or {}).items():
            try:
                module, class_name, class_loader = self.LOADERS[name]
                cls = getattr(importlib.import_module(module), class_name)
                if class_loader:
                    model = cls.load(path)
                    model.eval()
                else:
                    model = cls()
                    model.load(path)
                self.models[name] = model
            except Exception as exc:
                self.load_errors[name] = str(exc)

    def track_latency(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            started = time.perf_counter()
            try:
                return func(self, *args, **kwargs)
            finally:
                self.latency_stats.append((time.perf_counter() - started) * 1000)
        return wrapper

    @staticmethod
    def _input(model, features):
        if not isinstance(features, dict):
            return np.asarray(features, dtype=float)
        names = getattr(model, "feature_names", [])
        if not names:
            raise ValueError("Model artifact has no feature order; retrain with feature_names")
        missing = set(names) - features.keys()
        if missing:
            raise ValueError(f"Model requires unavailable features: {sorted(missing)}")
        return np.asarray([[features[name] for name in names]], dtype=float)

    @track_latency
    def infer_flow(self, flow_features):
        results = {"model_status": "unavailable", "errors": dict(self.load_errors)}
        for name in ("classifier", "anomaly"):
            if name not in self.models:
                continue
            model = self.models[name]
            try:
                features = self._input(model, flow_features)
                if name == "classifier":
                    results["attack_type"] = str(model.predict(features)[0])
                    results["confidence"] = float(np.max(model.predict_proba(features)[0]))
                else:
                    results["anomaly_score"] = float(model.score_samples(features)[0])
                results["model_status"] = "available"
            except Exception as exc:
                results["errors"][name] = str(exc)
        if results["errors"] and results["model_status"] == "available":
            results["model_status"] = "partial"
        return results

    @track_latency
    def infer_sequence(self, stages):
        if "sequence" in self.models:
            indices, probabilities = self.models["sequence"].predict_top_k(stages)
            return {"next_stages": indices.tolist(), "probs": probabilities.tolist()}
        return {"model_status": "unavailable"}
