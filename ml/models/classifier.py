import xgboost as xgb
import joblib
import numpy as np
from typing import List, Tuple, Dict, Any

class FlowClassifier:
    """XGBoost multi-class classifier for network flows."""

    def __init__(self):
        self.model = xgb.XGBClassifier(
            objective='multi:softprob',
            eval_metric='mlogloss',
            use_label_encoder=False,
            tree_method='hist'
        )
        self.label_mapping = {}
        self.reverse_label_mapping = {}
        self.feature_names = []

    def fit(self, X: np.ndarray, y: np.ndarray, feature_names: List[str] = None):
        """Train the classifier."""
        # Encode labels
        unique_labels = np.unique(y)
        if len(unique_labels) < 2:
            raise ValueError("Classifier training requires at least two classes")
        self.model.set_params(objective='binary:logistic' if len(unique_labels) == 2 else 'multi:softprob',
                              eval_metric='logloss' if len(unique_labels) == 2 else 'mlogloss')
        self.label_mapping = {label: idx for idx, label in enumerate(unique_labels)}
        self.reverse_label_mapping = {idx: label for label, idx in self.label_mapping.items()}
        
        y_encoded = np.array([self.label_mapping[label] for label in y])
        
        if feature_names:
            self.feature_names = feature_names
            
        self.model.fit(X, y_encoded)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict_proba(X)

    def predict(self, X: np.ndarray) -> List[str]:
        preds = self.model.predict(X)
        return [self.reverse_label_mapping.get(p, "UNKNOWN") for p in preds]

    def predict_top_k(self, X: np.ndarray, k: int = 3) -> List[List[Tuple[str, float]]]:
        """Return Top-K predictions with probabilities."""
        probas = self.predict_proba(X)
        results = []
        for prob in probas:
            top_k_idx = np.argsort(prob)[-k:][::-1]
            results.append([
                (self.reverse_label_mapping.get(idx, "UNKNOWN"), float(prob[idx]))
                for idx in top_k_idx
            ])
        return results

    def get_feature_importance(self) -> Dict[str, float]:
        if not self.feature_names:
            return {}
        importances = self.model.feature_importances_
        return {name: float(imp) for name, imp in zip(self.feature_names, importances)}

    def save(self, filepath: str):
        joblib.dump({
            'model': self.model,
            'label_mapping': self.label_mapping,
            'reverse_label_mapping': self.reverse_label_mapping,
            'feature_names': self.feature_names
        }, filepath)

    def load(self, filepath: str):
        data = joblib.load(filepath)
        self.model = data['model']
        self.label_mapping = data['label_mapping']
        self.reverse_label_mapping = data['reverse_label_mapping']
        self.feature_names = data.get('feature_names', [])
