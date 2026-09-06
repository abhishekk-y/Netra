import torch
import torch.nn as nn
import numpy as np

class BehaviorAutoencoder(nn.Module):
    """Dense autoencoder for host behavior vectors."""

    def __init__(self, input_dim: int, threshold: float = None):
        super(BehaviorAutoencoder, self).__init__()
        self.input_dim = input_dim
        self.threshold = threshold
        
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 16),
            nn.ReLU()
        )
        
        self.decoder = nn.Sequential(
            nn.Linear(16, 32),
            nn.ReLU(),
            nn.Linear(32, 64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, input_dim)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        encoded = self.encoder(x)
        decoded = self.decoder(encoded)
        return decoded

    def compute_anomaly_score(self, x: torch.Tensor) -> torch.Tensor:
        """Returns MSE reconstruction error as anomaly score."""
        self.eval()
        with torch.no_grad():
            reconstructed = self(x)
            mse = torch.mean((x - reconstructed) ** 2, dim=1)
        return mse

    def fit_threshold(self, normal_data: np.ndarray, percentile: float = 95.0):
        """Calculate and set the threshold based on normal data validation."""
        x_tensor = torch.FloatTensor(normal_data)
        scores = self.compute_anomaly_score(x_tensor).numpy()
        self.threshold = float(np.percentile(scores, percentile))
        return self.threshold

    def is_anomalous(self, x: torch.Tensor) -> torch.Tensor:
        if self.threshold is None:
            raise ValueError("Threshold not set. Call fit_threshold first.")
        scores = self.compute_anomaly_score(x)
        return scores > self.threshold

    def save(self, filepath: str):
        torch.save({
            'state_dict': self.state_dict(),
            'input_dim': self.input_dim,
            'threshold': self.threshold
        }, filepath)

    @classmethod
    def load(cls, filepath: str):
        data = torch.load(filepath, map_location='cpu', weights_only=True)
        model = cls(input_dim=data['input_dim'], threshold=data['threshold'])
        model.load_state_dict(data['state_dict'])
        model.eval()
        return model
