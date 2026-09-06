import argparse
import pandas as pd
from ml.models.anomaly import AnomalyDetector
from ml.datasets.adapters.cicids2017 import CICIDS2017Adapter

def main():
    parser = argparse.ArgumentParser(description="Train Isolation Forest")
    parser.add_argument("--data", type=str, required=True, help="Path to data")
    parser.add_argument("--output", type=str, default="anomaly_detector.pkl")
    args = parser.parse_args()

    adapter = CICIDS2017Adapter()
    df = adapter.load(args.data)
    features_df = adapter.to_features(df)
    
    # Train only on BENIGN
    train_df = features_df[features_df['label'] == 'BENIGN']
    feature_cols = [c for c in train_df.columns if c not in ['label', 'timestamp']]
    X_train = train_df[feature_cols].values

    detector = AnomalyDetector(contamination=0.01)
    print("Training Isolation Forest...")
    if not len(X_train) or not feature_cols:
        parser.error("Dataset has no BENIGN rows or usable flow features")
    detector.fit(X_train, feature_names=feature_cols)

    detector.save(args.output)
    print(f"Saved to {args.output}")

if __name__ == "__main__":
    main()
