import numpy as np
import joblib
from sklearn.ensemble import IsolationForest
from typing import Dict, Any

class AnomalyDetector:
    """Isolation Forest for unsupervised anomaly detection."""

    def __init__(self, contamination: float = 0.01):
        self.contamination = contamination
        self.feature_names = []
        self.model = IsolationForest(
            n_estimators=100, 
            contamination=self.contamination, 
            random_state=42
        )

    def fit(self, X: np.ndarray, feature_names=None):
        """Train on 'normal' traffic features."""
        self.model.fit(X)
        self.feature_names = list(feature_names or [])

    def score_samples(self, X: np.ndarray) -> np.ndarray:
        """Produce anomaly scores 0-100 (higher = more anomalous)."""
        # score_samples returns negative anomaly score (lower is more anomalous)
        # We invert and scale it to 0-100
        scores = self.model.score_samples(X)
        # Normalize between 0 and 100 based on standard IsolationForest bounds
        # scores typically range between -1 and 0
        normalized = (1 - ((scores + 1) / 1)) * 100
        return np.clip(normalized, 0, 100)
        
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Returns 1 for anomaly, 0 for normal."""
        preds = self.model.predict(X)
        # IF returns -1 for anomaly, 1 for normal
        return np.where(preds == -1, 1, 0)

    def save(self, filepath: str):
        joblib.dump({
            'model': self.model,
            'contamination': self.contamination
            , 'feature_names': self.feature_names
        }, filepath)

    def load(self, filepath: str):
        data = joblib.load(filepath)
        self.model = data['model']
        self.contamination = data['contamination']
        self.feature_names = data.get('feature_names', [])
