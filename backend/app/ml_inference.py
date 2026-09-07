"""Optional inference from a trusted administrator-installed local artifact.

Pickles are executable objects: NETRA_ENABLE_ML must opt in. API uploads never
become model paths. The bundled trainer uses synthetic data; its scores do not
establish performance on captured traffic and its outputs are not calibrated.
"""
from __future__ import annotations
import logging
import os
from pathlib import Path
from threading import RLock

logger = logging.getLogger(__name__)
_artifact = None
_attempted = False
_load_error = None
_lock = RLock()
_ARTIFACT_PATH = Path(__file__).resolve().parent / "models" / "nx_tfr_ensemble.pkl"
# Also accept the legacy path if the preferred path is absent
_ARTIFACT_PATH_FALLBACK = Path(__file__).resolve().parents[1] / "models" / "nx_tfr_ensemble.pkl"
FEATURE_NAMES = [
    'duration', 'srcPort', 'dstPort', 'protocol_tcp', 'protocol_udp',
    'protocol_icmp', 'bytes', 'packets', 'bytes_per_packet', 'packets_per_sec',
    'bytes_per_sec', 'dst_is_private', 'dst_is_external', 'src_is_external',
    'port_is_privileged', 'port_is_well_known', 'port_is_high',
    'app_ssh', 'app_http', 'app_https', 'app_smb', 'app_rdp', 'app_dns',
]

def _enabled():
    # ML is enabled by default when the artifact file exists.
    # Set NETRA_ENABLE_ML=false to explicitly disable.
    return os.getenv("NETRA_ENABLE_ML", "true").lower() != "false"

def _load_artifact():
    global _artifact, _attempted, _load_error
    if not _enabled():
        return None
    with _lock:
        if _attempted:
            return _artifact
        _attempted = True
        # Prefer backend/app/models/, fall back to backend/models/
        path = _ARTIFACT_PATH if _ARTIFACT_PATH.is_file() else _ARTIFACT_PATH_FALLBACK
        if not path.is_file():
            _load_error = "Trusted local model artifact not found"
            return None
        try:
            import joblib
            candidate = joblib.load(path)
            required = {"scaler", "ensemble", "anomaly_detector", "class_names", "feature_names"}
            if not isinstance(candidate, dict) or not required <= candidate.keys():
                raise ValueError("Unsupported artifact structure")
            if list(candidate["feature_names"]) != FEATURE_NAMES:
                raise ValueError("Artifact feature order does not match this runtime")
            if not candidate["class_names"]:
                raise ValueError("Artifact contains no class labels")
            _artifact = candidate
        except Exception as exc:
            _load_error = f"Model unavailable: {type(exc).__name__}"
            logger.warning("Local ML artifact could not be loaded: %s", exc)
        return _artifact

def extract_features(flow):
    import numpy as np
    from ipaddress import ip_address
    dur = max(float(flow.get("duration", 0) or 0), .001)
    src_port, dst_port = int(flow.get("srcPort", 0)), int(flow.get("dstPort", 0))
    proto = str(flow.get("protocol", "")).upper()
    bytes_n, packets_n = float(flow.get("bytes", 0)), float(flow.get("packets", 0))
    dst_private, src_private = ip_address(flow["dstIp"]).is_private, ip_address(flow["srcIp"]).is_private
    return np.asarray([
        dur, src_port, dst_port, proto == "TCP", proto == "UDP", proto == "ICMP",
        bytes_n, packets_n, bytes_n / max(packets_n, 1), packets_n / dur, bytes_n / dur,
        dst_private, not dst_private, not src_private, dst_port < 1024,
        dst_port in (22, 53, 80, 443, 445, 3389), dst_port > 10000,
        dst_port == 22, dst_port == 80, dst_port == 443, dst_port == 445,
        dst_port == 3389, dst_port == 53,
    ], dtype=np.float32)

def _unavailable(reason=None):
    return {"mlRiskScore": 5, "mlAttackType": None, "mlConfidence": 0.0,
            "mlAnomalyScore": 0.0, "mlAvailable": False, "mlCalibrated": False,
            "mlMethod": "unavailable", "mlReason": reason or _load_error or "ML disabled; set NETRA_ENABLE_ML=true for a trusted local artifact",
            "mlTrainingData": "not loaded"}

def predict_flow(flow):
    artifact = _load_artifact()
    if artifact is None:
        return _unavailable()
    try:
        import numpy as np
        features = extract_features(flow).reshape(1, -1)
        if not np.isfinite(features).all():
            return _unavailable("Nonfinite model features")
        scaled = artifact["scaler"].transform(features)
        ensemble = artifact["ensemble"]
        index = int(ensemble.predict(scaled)[0])
        probabilities = np.asarray(ensemble.predict_proba(scaled)[0], dtype=float)
        if not np.isfinite(probabilities).all():
            return _unavailable("Nonfinite model scores")
        confidence = float(np.clip(probabilities.max(), 0, 1))
        label = str(artifact["class_names"][index])
        detector = artifact["anomaly_detector"]
        # IsolationForest decision_function has a documented zero threshold.
        # This linear transform is a display priority only, not a probability.
        margin = float(detector.decision_function(scaled)[0])
        if not np.isfinite(margin):
            return _unavailable("Nonfinite anomaly margin")
        anomaly = float(np.clip(-margin * 200, 0, 100))
        risk = max(5.0, anomaly * .3) if label.casefold() == "benign" else float(np.clip(confidence * 90 + anomaly * .1, 10, 99))
        return {"mlRiskScore": round(risk, 1), "mlAttackType": None if label.casefold() == "benign" else label,
                "mlConfidence": round(confidence, 4), "mlAnomalyScore": round(anomaly, 2),
                "mlAnomalyMargin": margin, "mlAvailable": True, "mlCalibrated": False,
                "mlMethod": "local-ensemble-uncalibrated",
                "mlTrainingData": artifact.get("training_data", "Synthetic reference trainer; artifact dataset provenance unverified")}
    except Exception as exc:
        logger.warning("ML prediction unavailable: %s", exc)
        return _unavailable(f"Prediction failed: {type(exc).__name__}")

def get_model_status():
    artifact = _load_artifact()
    base = {"available": artifact is not None, "enabled": _enabled(), "calibrated": False,
            "validationScope": "Artifact-reported metrics; no independently verified real-traffic benchmark",
            "trainingData": "Synthetic reference trainer; artifact dataset provenance unverified"}
    if artifact is None:
        return {**base, "version": None, "trainedAt": None, "accuracy": None, "f1": None,
                "classes": [], "reason": _load_error or "ML disabled"}
    metrics = artifact.get("metrics", {})
    return {**base, "version": artifact.get("version"), "trainedAt": artifact.get("trained_at"),
            "accuracy": metrics.get("accuracy"), "f1": metrics.get("f1_weighted"),
            "classes": list(artifact["class_names"]), "featureCount": len(FEATURE_NAMES),
            "nTrain": metrics.get("n_train"), "nTest": metrics.get("n_test")}
