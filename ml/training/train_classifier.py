import argparse
import numpy as np
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix
from ml.datasets.adapters.cicids2017 import CICIDS2017Adapter
from ml.datasets.quality import DatasetQualityAnalyzer
from ml.models.classifier import FlowClassifier

def main():
    parser = argparse.ArgumentParser(description="Train XGBoost Flow Classifier")
    parser.add_argument("--data", type=str, required=True, help="Path to CICIDS2017 CSV")
    parser.add_argument("--output", type=str, default="flow_classifier.pkl", help="Output model path")
    parser.add_argument("--allow-row-order", action="store_true", help="Explicitly allow an unverified row-order holdout when timestamps are absent")
    args = parser.parse_args()

    # Load
    print(f"Loading data from {args.data}...")
    adapter = CICIDS2017Adapter()
    df = adapter.load(args.data)
    
    # Feature map
    features_df = adapter.to_features(df)
    
    # Quality Analysis
    analyzer = DatasetQualityAnalyzer()
    report = analyzer.analyze(features_df, label_col='label')
    print("Dataset Quality Report:", report)

    # Need a dummy time column for temporal split if it doesn't exist, normally CIC-IDS has timestamp
    if 'Timestamp' in df.columns:
        features_df['timestamp'] = pd.to_datetime(df['Timestamp'], errors='raise')
    else:
        if not args.allow_row_order:
            parser.error("Timestamp is required for temporal evaluation; --allow-row-order explicitly opts into an unverified ordered holdout")
        print("WARNING: row-order holdout is not a validated temporal split.")
        features_df['timestamp'] = range(len(features_df))

    # Split
    train_df, test_df = analyzer.temporal_split(features_df, 'timestamp', 0.2)
    print(f"Train size: {len(train_df)}, Test size: {len(test_df)}")

    # Prepare data
    feature_cols = [c for c in train_df.columns if c not in ['label', 'timestamp']]
    X_train = train_df[feature_cols].values
    y_train = train_df['label'].values
    
    X_test = test_df[feature_cols].values
    y_test = test_df['label'].values

    # Train
    clf = FlowClassifier()
    print("Training Flow Classifier...")
    clf.fit(X_train, y_train, feature_names=feature_cols)

    # Eval
    print("Evaluating...")
    preds = clf.predict(X_test)
    
    print("Classification Report:")
    print(classification_report(y_test, preds))
    
    print("Confusion Matrix:")
    print(confusion_matrix(y_test, preds))

    # Save
    clf.save(args.output)
    print(f"Model saved to {args.output}")

if __name__ == "__main__":
    main()
