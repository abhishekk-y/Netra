import torch
import torch.nn as nn
import torch.nn.functional as F

class TargetPredictor(nn.Module):
    """Predicts which host is most likely to be targeted next."""

    def __init__(self, feature_dim: int):
        super(TargetPredictor, self).__init__()
        self.feature_dim = feature_dim
        
        # Input features: host_features + graph_features + attack_context
        self.mlp = nn.Sequential(
            nn.Linear(feature_dim, 128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1) # Output probability score
        )

    def forward(self, x: torch.Tensor):
        """
        x: (batch, num_hosts, feature_dim)
        """
        batch_size, num_hosts, f_dim = x.shape
        # Flatten to process each host
        x_flat = x.reshape(-1, f_dim)
        
        scores = self.mlp(x_flat)
        scores = scores.view(batch_size, num_hosts)
        
        # Softmax over hosts to get probability
        probs = F.softmax(scores, dim=1)
        return probs

    def save(self, filepath: str):
        torch.save({
            'state_dict': self.state_dict(),
            'feature_dim': self.feature_dim
        }, filepath)

    @classmethod
    def load(cls, filepath: str):
        data = torch.load(filepath, map_location='cpu', weights_only=True)
        model = cls(feature_dim=data['feature_dim'])
        model.load_state_dict(data['state_dict'])
        model.eval()
        return model
