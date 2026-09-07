"""
Netra-X ML Inference Module
Loads the trained ensemble artifact and provides live prediction.
"""
from __future__ import annotations
import logging
import numpy as np
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Lazy-load joblib to avoid import overhead at startup
_artifact: Optional[dict] = None
_ARTIFACT_PATH = Path(__file__).resolve().parents[1] / "models" / "nx_tfr_ensemble.pkl"

FEATURE_NAMES = [
    'duration', 'srcPort', 'dstPort', 'protocol_tcp', 'protocol_udp',
    'protocol_icmp', 'bytes', 'packets', 'bytes_per_packet', 'packets_per_sec',
    'bytes_per_sec', 'dst_is_private', 'dst_is_external', 'src_is_external',
    'port_is_privileged', 'port_is_well_known', 'port_is_high',
    'app_ssh', 'app_http', 'app_https', 'app_smb', 'app_rdp', 'app_dns',
]


def _load_artifact() -> Optional[dict]:
    global _artifact
    if _artifact is not None:
        return _artifact
    if not _ARTIFACT_PATH.exists():
        logger.warning("ML artifact not found at %s; heuristic scoring only.", _ARTIFACT_PATH)
        return None
    try:
        import joblib
        _artifact = joblib.load(_ARTIFACT_PATH)
        meta = _artifact.get('metrics', {})
        logger.info(
            "ML ensemble loaded — accuracy=%.2f%% f1=%.2f%% classes=%s",
            meta.get('accuracy', 0) * 100,
            meta.get('f1_weighted', 0) * 100,
            meta.get('classes', []),
        )
        return _artifact
    except Exception as exc:
        logger.error("Failed to load ML artifact: %s", exc)
        return None


def _is_private(ip: str) -> bool:
    try:
        from ipaddress import ip_address
        return ip_address(ip).is_private
    except Exception:
        return True


def extract_features(flow: dict) -> np.ndarray:
    """Extract feature vector from a raw flow dict."""
    dur = max(float(flow.get('duration', 0.001) or 0.001), 0.001)
    src_port = int(flow.get('srcPort', 0) or 0)
    dst_port = int(flow.get('dstPort', 0) or 0)
    proto = str(flow.get('protocol', '')).upper()
    bytes_n = float(flow.get('bytes', 0) or 0)
    packets_n = max(float(flow.get('packets', 1) or 1), 1)
    dst_ip = str(flow.get('dstIp', '') or '')
    src_ip = str(flow.get('srcIp', '') or '')

    dst_priv = _is_private(dst_ip)
    src_priv = _is_private(src_ip)

    return np.array([
        dur,
        src_port,
        dst_port,
        1 if proto == 'TCP' else 0,
        1 if proto == 'UDP' else 0,
        1 if proto == 'ICMP' else 0,
        bytes_n,
        packets_n,
        bytes_n / packets_n,
        packets_n / dur,
        bytes_n / dur,
        1 if dst_priv else 0,
        0 if dst_priv else 1,
        0 if src_priv else 1,
        1 if dst_port < 1024 else 0,
        1 if dst_port in (22, 53, 80, 443, 445, 3389) else 0,
        1 if dst_port > 10000 else 0,
        1 if dst_port == 22 else 0,
        1 if dst_port == 80 else 0,
        1 if dst_port == 443 else 0,
        1 if dst_port == 445 else 0,
        1 if dst_port == 3389 else 0,
        1 if dst_port == 53 else 0,
    ], dtype=np.float32)


def predict_flow(flow: dict) -> dict:
    """
    Run ML inference on a flow dict.
    Returns:
        {
          'mlRiskScore': float (0-100),
          'mlAttackType': str,
          'mlConfidence': float (0-1),
          'mlAnomalyScore': float,
          'mlAvailable': bool,
        }
    """
    artifact = _load_artifact()
    if artifact is None:
        return {
            'mlRiskScore': 5,
            'mlAttackType': 'Unknown',
            'mlConfidence': 0.0,
            'mlAnomalyScore': 0.0,
            'mlAvailable': False,
        }

    try:
        feats = extract_features(flow).reshape(1, -1)
        scaler = artifact['scaler']
        ensemble = artifact['ensemble']
        iso = artifact['anomaly_detector']
        class_names = artifact['class_names']

        feats_scaled = scaler.transform(feats)

        # Classification
        pred_class_idx = ensemble.predict(feats_scaled)[0]
        proba = ensemble.predict_proba(feats_scaled)[0]
        confidence = float(np.max(proba))
        predicted_class = class_names[int(pred_class_idx)]

        # Anomaly score (normalized 0-100, higher = more anomalous)
        raw_score = float(iso.score_samples(feats_scaled)[0])
        # Isolation Forest: lower score = more anomalous (range roughly -0.5 to 0.5)
        anomaly_normalized = float(np.clip((0.5 - raw_score) * 100, 0, 100))

        # Risk score: blend ML confidence of malicious class + anomaly signal
        if predicted_class == 'Benign':
            risk_score = max(5.0, anomaly_normalized * 0.3)
        else:
            risk_score = float(np.clip(confidence * 90 + anomaly_normalized * 0.1, 10, 99))

        return {
            'mlRiskScore': round(risk_score, 1),
            'mlAttackType': predicted_class if predicted_class != 'Benign' else None,
            'mlConfidence': round(confidence, 4),
            'mlAnomalyScore': round(anomaly_normalized, 2),
            'mlAvailable': True,
        }

    except Exception as exc:
        logger.error("ML inference error: %s", exc)
        return {
            'mlRiskScore': 5,
            'mlAttackType': 'Unknown',
            'mlConfidence': 0.0,
            'mlAnomalyScore': 0.0,
            'mlAvailable': False,
        }


def get_model_status() -> dict:
    """Return metadata about the loaded model."""
    artifact = _load_artifact()
    if artifact is None:
        return {
            'available': False,
            'version': None,
            'trainedAt': None,
            'accuracy': None,
            'f1': None,
            'classes': [],
            'artifactPath': str(_ARTIFACT_PATH),
        }
    metrics = artifact.get('metrics', {})
    return {
        'available': True,
        'version': artifact.get('version', '1.0'),
        'trainedAt': artifact.get('trained_at'),
        'accuracy': metrics.get('accuracy'),
        'f1': metrics.get('f1_weighted'),
        'classes': artifact.get('class_names', []),
        'featureCount': len(artifact.get('feature_names', [])),
        'artifactPath': str(_ARTIFACT_PATH),
        'nTrain': metrics.get('n_train'),
        'nTest': metrics.get('n_test'),
    }
