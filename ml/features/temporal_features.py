import numpy as np
from typing import List, Dict, Any, Tuple

class TemporalFeatureExtractor:
    """Extracts sequence features for time-series and temporal models."""
    
    def __init__(self, sequence_length: int = 20, num_stages: int = 6):
        self.seq_len = sequence_length
        self.num_stages = num_stages

    def create_sliding_windows(self, features: np.ndarray, labels: np.ndarray = None, step: int = 1) -> Tuple[np.ndarray, np.ndarray]:
        """
        Create sliding windows of feature vectors.
        features: (N, D) array
        labels: (N,) array or None
        """
        N = len(features)
        if N < self.seq_len:
            # Pad if too short
            pad_size = self.seq_len - N
            features = np.pad(features, ((pad_size, 0), (0, 0)), mode='constant')
            if labels is not None:
                labels = np.pad(labels, (pad_size, 0), mode='constant')
            N = self.seq_len

        windows = []
        window_labels = []
        for i in range(0, N - self.seq_len + 1, step):
            windows.append(features[i:i + self.seq_len])
            if labels is not None:
                window_labels.append(labels[i + self.seq_len - 1]) # Label of the last element

        out_features = np.array(windows)
        out_labels = np.array(window_labels) if labels is not None else None
        
        return out_features, out_labels

    def encode_attack_sequence(self, stages: List[int]) -> np.ndarray:
        """
        Encode a sequence of attack stages with padding if necessary.
        Uses 0 for padding.
        """
        seq = np.zeros(self.seq_len, dtype=np.int64)
        if not stages:
            return seq
            
        stages = stages[-self.seq_len:]
        seq[-len(stages):] = stages
        return seq

    def normalize_features(self, features: np.ndarray, eps: float = 1e-8) -> np.ndarray:
        """
        Standard scale the feature dimensions.
        """
        mean = np.mean(features, axis=(0, 1), keepdims=True)
        std = np.std(features, axis=(0, 1), keepdims=True)
        return (features - mean) / (std + eps)
