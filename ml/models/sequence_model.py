import torch
import torch.nn as nn
import torch.nn.functional as F

class SequenceForecaster(nn.Module):
    """GRU-based model for next attack stage prediction."""

    def __init__(self, num_stages: int, embed_dim: int = 32, hidden_dim: int = 128, num_layers: int = 2):
        super(SequenceForecaster, self).__init__()
        self.num_stages = num_stages
        self.embed_dim, self.hidden_dim, self.num_layers = embed_dim, hidden_dim, num_layers
        
        # We add +1 for padding (index 0)
        self.embedding = nn.Embedding(num_embeddings=num_stages + 1, embedding_dim=embed_dim, padding_idx=0)
        
        self.gru = nn.GRU(
            input_size=embed_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=0.3 if num_layers > 1 else 0
        )
        
        self.fc = nn.Linear(hidden_dim, num_stages)

    def forward(self, x: torch.Tensor, hidden: torch.Tensor = None):
        """
        x: (batch, seq_len) of attack stages
        """
        embedded = self.embedding(x)
        output, hidden = self.gru(embedded, hidden)
        
        # Take the output of the last time step
        last_out = output[:, -1, :]
        logits = self.fc(last_out)
        
        return logits, hidden

    def predict_top_k(self, x: torch.Tensor, k: int = 3, temperature: float = 1.0):
        if k < 1 or temperature <= 0:
            raise ValueError("k and temperature must be positive")
        k = min(k, self.num_stages)
        self.eval()
        with torch.no_grad():
            logits, _ = self(x)
            # Apply temperature scaling
            scaled_logits = logits / temperature
            probs = F.softmax(scaled_logits, dim=-1)
            
            top_probs, top_indices = torch.topk(probs, k, dim=-1)
            
        return top_indices, top_probs

    def save(self, filepath: str):
        torch.save({
            'state_dict': self.state_dict(),
            'num_stages': self.num_stages,
            'embed_dim': self.embed_dim, 'hidden_dim': self.hidden_dim, 'num_layers': self.num_layers,
        }, filepath)

    @classmethod
    def load(cls, filepath: str):
        data = torch.load(filepath, map_location='cpu', weights_only=True)
        model = cls(num_stages=data['num_stages'], embed_dim=data.get('embed_dim', 32),
                    hidden_dim=data.get('hidden_dim', 128), num_layers=data.get('num_layers', 2))
        model.load_state_dict(data['state_dict'])
        model.eval()
        return model
