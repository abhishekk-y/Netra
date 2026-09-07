"""
Netra-X ML Ensemble Training Script
Trains a flow classifier on supplied measured features or explicitly synthetic examples.
This is detection, not future-event forecasting. Synthetic metrics establish only
agreement with this generator and cannot establish real-world attack accuracy.
Usage:
    python -m ml.training.train_ensemble --data measured_features.csv
    python -m ml.training.train_ensemble --synthetic --samples 5000
"""
import os
import argparse
import hashlib
import sys
import time
import numpy as np
import pandas as pd
import joblib
from pathlib import Path

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import (
    RandomForestClassifier, GradientBoostingClassifier,
    VotingClassifier, IsolationForest
)
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (
    classification_report, accuracy_score, f1_score,
    roc_auc_score, confusion_matrix
)
import xgboost as xgb

ROOT = Path(__file__).resolve().parents[2]
OUT_PATH = ROOT / "ml" / "artifacts" / "flow_ensemble.pkl"

# ─────────────────────────────────────────────────────────────────────────────
# FEATURE SCHEMA
# These 23 features map directly to what runtime.py extracts from ingested flows
# ─────────────────────────────────────────────────────────────────────────────
FEATURE_NAMES = [
    'duration', 'srcPort', 'dstPort', 'protocol_tcp', 'protocol_udp',
    'protocol_icmp', 'bytes', 'packets', 'bytes_per_packet', 'packets_per_sec',
    'bytes_per_sec', 'dst_is_private', 'dst_is_external', 'src_is_external',
    'port_is_privileged', 'port_is_well_known', 'port_is_high',
    'app_ssh', 'app_http', 'app_https', 'app_smb', 'app_rdp', 'app_dns',
]

ATTACK_CLASSES = [
    'Benign',
    'Reconnaissance',
    'Lateral Movement',
    'Exfiltration',
    'Impact',
    'Credential Access',
    'Command and Control',
]

# ─────────────────────────────────────────────────────────────────────────────
# SYNTHETIC DATA GENERATOR
# Illustrative distributions chosen by hand; not a benchmark dataset.
# ─────────────────────────────────────────────────────────────────────────────
def generate_synthetic_dataset(n_samples: int = 120_000, seed: int = 42) -> pd.DataFrame:
    if n_samples < 100:
        raise ValueError("Synthetic demonstrations need at least 100 samples")
    rng = np.random.default_rng(seed)
    records = []

    class_configs = {
        'Benign': {
            'n': int(n_samples * 0.65),
            'duration': (1, 30),
            'bytes': (500, 50_000),
            'packets': (5, 200),
            'dst_ports': [80, 443, 53, 8080, 8443],
            'protocols': ['TCP', 'UDP'],
        },
        'Reconnaissance': {
            'n': int(n_samples * 0.08),
            'duration': (0.01, 0.5),
            'bytes': (40, 500),
            'packets': (1, 5),
            'dst_ports': [21, 22, 23, 25, 80, 135, 139, 389, 443, 445, 1433, 3389],
            'protocols': ['TCP'],
        },
        'Lateral Movement': {
            'n': int(n_samples * 0.07),
            'duration': (0.5, 20),
            'bytes': (10_000, 200_000),
            'packets': (20, 500),
            'dst_ports': [445, 3389, 135, 139],
            'protocols': ['TCP'],
        },
        'Exfiltration': {
            'n': int(n_samples * 0.06),
            'duration': (5, 120),
            'bytes': (1_000_000, 50_000_000),
            'packets': (100, 5000),
            'dst_ports': [443, 80, 53, 21, 22],
            'protocols': ['TCP'],
        },
        'Impact': {
            'n': int(n_samples * 0.05),
            'duration': (0.001, 10),
            'bytes': (50, 1500),
            'packets': (1000, 100_000),
            'dst_ports': [80, 443, 53],
            'protocols': ['TCP', 'UDP'],
        },
        'Credential Access': {
            'n': int(n_samples * 0.05),
            'duration': (0.01, 2),
            'bytes': (200, 2000),
            'packets': (3, 30),
            'dst_ports': [22, 21, 3389, 23, 25],
            'protocols': ['TCP'],
        },
        'Command and Control': {
            'n': int(n_samples * 0.04),
            'duration': (30, 3600),
            'bytes': (100, 10_000),
            'packets': (5, 100),
            'dst_ports': [53, 80, 443, 4444, 8080, 8443, 6667],
            'protocols': ['TCP', 'UDP'],
        },
    }

    for label, cfg in class_configs.items():
        n = cfg['n']
        durations = rng.uniform(*cfg['duration'], size=n)
        bytes_arr = rng.uniform(*cfg['bytes'], size=n)
        packets_arr = rng.integers(cfg['packets'][0], max(cfg['packets'][1], cfg['packets'][0]+1), size=n).astype(float)
        dst_ports = rng.choice(cfg['dst_ports'], size=n)
        protocols = rng.choice(cfg['protocols'], size=n)
        src_ports = rng.integers(1025, 65535, size=n)

        # Private/external IPs
        dst_is_private = rng.random(size=n) > (0.3 if label in ('Exfiltration', 'Command and Control') else 0.7)
        src_is_external = rng.random(size=n) > (0.7 if label in ('Credential Access', 'Reconnaissance') else 0.9)

        for i in range(n):
            dur = max(durations[i], 0.001)
            bpp = bytes_arr[i] / max(packets_arr[i], 1)
            pps = packets_arr[i] / dur
            bps = bytes_arr[i] / dur
            proto = protocols[i]
            dport = int(dst_ports[i])

            records.append({
                'duration': dur,
                'srcPort': int(src_ports[i]),
                'dstPort': dport,
                'protocol_tcp': 1 if proto == 'TCP' else 0,
                'protocol_udp': 1 if proto == 'UDP' else 0,
                'protocol_icmp': 1 if proto == 'ICMP' else 0,
                'bytes': bytes_arr[i],
                'packets': packets_arr[i],
                'bytes_per_packet': bpp,
                'packets_per_sec': pps,
                'bytes_per_sec': bps,
                'dst_is_private': 1 if dst_is_private[i] else 0,
                'dst_is_external': 0 if dst_is_private[i] else 1,
                'src_is_external': 1 if src_is_external[i] else 0,
                'port_is_privileged': 1 if dport < 1024 else 0,
                'port_is_well_known': 1 if dport in (22, 53, 80, 443, 445, 3389) else 0,
                'port_is_high': 1 if dport > 10000 else 0,
                'app_ssh': 1 if dport == 22 else 0,
                'app_http': 1 if dport == 80 else 0,
                'app_https': 1 if dport == 443 else 0,
                'app_smb': 1 if dport == 445 else 0,
                'app_rdp': 1 if dport == 3389 else 0,
                'app_dns': 1 if dport == 53 else 0,
                'label': label,
            })

    df = pd.DataFrame(records)
    df = df.sample(frac=1.0, random_state=seed).reset_index(drop=True)
    print(f"  Generated {len(df):,} samples | Classes: {df['label'].value_counts().to_dict()}")
    return df


# ─────────────────────────────────────────────────────────────────────────────
# FEATURE EXTRACTOR (used by runtime.py for live inference)
# ─────────────────────────────────────────────────────────────────────────────
def extract_features(flow: dict) -> np.ndarray:
    """
    Extract the 23-dimensional feature vector from a raw flow dict.
    Compatible with both ingested flows and the training schema.
    """
    dur = max(float(flow.get('duration', 0) or 0), 0)
    src_port = int(flow.get('srcPort', 0) or 0)
    dst_port = int(flow.get('dstPort', 0) or 0)
    proto = str(flow.get('protocol', '')).upper()
    bytes_n = float(flow.get('bytes', 0) or 0)
    packets_n = max(float(flow.get('packets', 0) or 0), 0)
    dst_ip = str(flow.get('dstIp', ''))
    src_ip = str(flow.get('srcIp', ''))

    def is_private(ip: str) -> bool:
        try:
            from ipaddress import ip_address
            return ip_address(ip).is_private
        except Exception:
            return True

    dst_priv = is_private(dst_ip)
    src_priv = is_private(src_ip)

    return np.array([
        dur,                                        # 0 duration
        src_port,                                   # 1 srcPort
        dst_port,                                   # 2 dstPort
        1 if proto == 'TCP' else 0,                # 3 protocol_tcp
        1 if proto == 'UDP' else 0,                # 4 protocol_udp
        1 if proto == 'ICMP' else 0,               # 5 protocol_icmp
        bytes_n,                                    # 6 bytes
        packets_n,                                  # 7 packets
        bytes_n / packets_n if packets_n else 0,     # 8 bytes_per_packet
        packets_n / dur if dur else 0,               # 9 packets_per_sec
        bytes_n / dur if dur else 0,                 # 10 bytes_per_sec
        1 if dst_priv else 0,                      # 11 dst_is_private
        0 if dst_priv else 1,                      # 12 dst_is_external
        0 if src_priv else 1,                      # 13 src_is_external
        1 if dst_port < 1024 else 0,               # 14 port_is_privileged
        1 if dst_port in (22,53,80,443,445,3389) else 0,  # 15 port_is_well_known
        1 if dst_port > 10000 else 0,              # 16 port_is_high
        1 if dst_port == 22 else 0,                # 17 app_ssh
        1 if dst_port == 80 else 0,                # 18 app_http
        1 if dst_port == 443 else 0,               # 19 app_https
        1 if dst_port == 445 else 0,               # 20 app_smb
        1 if dst_port == 3389 else 0,              # 21 app_rdp
        1 if dst_port == 53 else 0,                # 22 app_dns
    ], dtype=np.float32)


# ─────────────────────────────────────────────────────────────────────────────
# TRAIN
# ─────────────────────────────────────────────────────────────────────────────
def train(data=None, *, synthetic=False, samples=5000, output=None):
    if (data is None) == (not synthetic):
        raise ValueError("Choose exactly one supplied data CSV or explicit synthetic mode")
    output_path = Path(output) if output else OUT_PATH.with_name("synthetic_flow_ensemble.pkl") if synthetic else OUT_PATH
    if output_path.exists():
        raise FileExistsError(f"Refusing to overwrite existing model: {output_path}")
    print("=" * 60)
    print("  NETRA-X ML ENSEMBLE TRAINING")
    print("=" * 60)

    # 1. Generate data
    print("\n[1/5] Preparing explicitly identified training data...")
    t0 = time.time()
    if synthetic:
        df = generate_synthetic_dataset(n_samples=samples)
        provenance = {"kind": "synthetic", "generator": "hand-authored-flow-distributions", "seed": 42}
        print("SYNTHETIC DEMO: results are not measured network detection or forecasting performance.")
    else:
        df = pd.read_csv(data)
        required = set(FEATURE_NAMES) | {"label", "timestamp"}
        if required - set(df):
            raise ValueError(f"Measured CSV is missing columns: {sorted(required - set(df))}")
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="raise", utc=True)
        df = df.sort_values("timestamp", kind="stable").reset_index(drop=True)
        provenance = {"kind": "user-supplied", "filename": Path(data).name,
                      "sha256": hashlib.sha256(Path(data).read_bytes()).hexdigest()}
    print(f"  Done in {time.time()-t0:.1f}s")

    # 2. Prepare features
    print("\n[2/5] Preparing features...")
    X = df[FEATURE_NAMES].values.astype(np.float32)
    if not np.isfinite(X).all() or df["label"].isna().any():
        raise ValueError("Training features and labels must be complete and finite")
    le = LabelEncoder()
    y = le.fit_transform(df['label'].values)
    class_names = le.classes_.tolist()
    print(f"  Feature matrix: {X.shape} | Classes: {class_names}")

    # 3. Split
    if synthetic:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y)
        split_method = "stratified-random-synthetic-holdout"
    else:
        from ml.datasets.quality import DatasetQualityAnalyzer
        train_frame, test_frame = DatasetQualityAnalyzer().temporal_split(df, "timestamp", .2)
        split = len(train_frame)
        X_train, X_test, y_train, y_test = X[:split], X[split:], y[:split], y[split:]
        split_method = "strict-timestamp-holdout"
        if len(np.unique(y_train)) != len(class_names):
            raise ValueError("Training interval does not contain every class; collect more training history")
    print(f"  Train: {len(X_train):,} | Test: {len(X_test):,}")

    # 4. Build ensemble
    print("\n[3/5] Training ML Ensemble...")
    t0 = time.time()

    xgb_clf = xgb.XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        use_label_encoder=False,
        eval_metric='mlogloss',
        random_state=42,
        n_jobs=-1,
        verbosity=0,
    )

    rf_clf = RandomForestClassifier(
        n_estimators=150,
        max_depth=8,
        min_samples_leaf=5,
        random_state=42,
        n_jobs=-1,
    )

    gb_clf = GradientBoostingClassifier(
        n_estimators=100,
        max_depth=5,
        learning_rate=0.1,
        random_state=42,
    )

    voting_clf = VotingClassifier(
        estimators=[
            ('xgb', xgb_clf),
            ('rf', rf_clf),
            ('gb', gb_clf),
        ],
        voting='soft',
        weights=[3, 2, 1],  # XGBoost weighted highest
        n_jobs=-1,
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    voting_clf.fit(X_train_scaled, y_train)
    print(f"  Ensemble trained in {time.time()-t0:.1f}s")

    # Also train anomaly detector
    print("  Training Isolation Forest anomaly detector...")
    iso = IsolationForest(
        n_estimators=100,
        contamination=0.15,
        random_state=42,
        n_jobs=-1,
    )
    iso.fit(X_train_scaled)

    # 5. Evaluate
    print("\n[4/5] Evaluating on test set...")
    y_pred = voting_clf.predict(X_test_scaled)
    y_proba = voting_clf.predict_proba(X_test_scaled)

    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average='weighted')

    print(f"\n  Accuracy:  {acc*100:.2f}%")
    print(f"  F1 Score:  {f1*100:.2f}%")
    print("\n  Classification Report:")
    print(classification_report(y_test, y_pred, target_names=class_names))

    # 6. Save
    print(f"\n[5/5] Saving model to {output_path}...")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    artifact = {
        'version': '2.0.0',
        'task': 'flow-classification',
        'forecasting_validated': False,
        'data_provenance': provenance,
        'evaluation_scope': 'synthetic-generator-holdout' if synthetic else 'user-supplied-temporal-holdout',
        'trained_at': pd.Timestamp.now().isoformat(),
        'feature_names': FEATURE_NAMES,
        'class_names': class_names,
        'label_encoder': le,
        'scaler': scaler,
        'ensemble': voting_clf,
        'anomaly_detector': iso,
        'metrics': {
            'split_method': split_method,
            'synthetic': synthetic,
            'accuracy': float(acc),
            'f1_weighted': float(f1),
            'n_train': len(X_train),
            'n_test': len(X_test),
            'classes': class_names,
        }
    }

    with output_path.open("xb") as stream:
        joblib.dump(artifact, stream, compress=3)
    size_kb = output_path.stat().st_size / 1024
    print(f"  Saved! Size: {size_kb:.1f} KB")

    print("\n" + "=" * 60)
    print(f"  TRAINING COMPLETE")
    print(f"  Accuracy: {acc*100:.2f}% | F1: {f1*100:.2f}%")
    print(f"  Model: {output_path}")
    print("  Evaluation concerns classification of these held-out flows, not future attacks.")
    print("=" * 60)

    return artifact


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Train a flow detector with explicit dataset provenance")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--data", help="CSV with the 23 documented features, label and timestamp")
    source.add_argument("--synthetic", action="store_true", help="Explicitly opt into synthetic demonstration training")
    parser.add_argument("--samples", type=int, default=5000)
    parser.add_argument("--output", help="New artifact path; existing artifacts are never overwritten")
    args = parser.parse_args()
    train(args.data, synthetic=args.synthetic, samples=args.samples, output=args.output)
