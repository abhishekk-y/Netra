import torch
import torch.nn as nn
import torch.nn.functional as F

class TemporalForecaster(nn.Module):
    """LSTM-based model for multi-horizon attack forecasting."""

    def __init__(self, input_dim: int, num_classes: int, hidden_dim: int = 256, num_layers: int = 2):
        super(TemporalForecaster, self).__init__()
        self.input_dim = input_dim
        self.num_classes = num_classes
        self.hidden_dim, self.num_layers = hidden_dim, num_layers
        
        self.lstm = nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=0.3 if num_layers > 1 else 0
        )
        
        # Attention mechanism
        self.attention = nn.Linear(hidden_dim, 1)
        
        # Multi-head outputs for different horizons (T+10s, T+30s, T+1m, T+5m)
        self.head_10s = nn.Linear(hidden_dim, num_classes)
        self.head_30s = nn.Linear(hidden_dim, num_classes)
        self.head_1m = nn.Linear(hidden_dim, num_classes)
        self.head_5m = nn.Linear(hidden_dim, num_classes)

    def forward(self, x: torch.Tensor):
        """
        x: (batch, seq_len, input_dim)
        """
        lstm_out, _ = self.lstm(x)  # (batch, seq_len, hidden_dim)
        
        # Attention weights over sequence
        attn_weights = F.softmax(self.attention(lstm_out), dim=1) # (batch, seq_len, 1)
        
        # Context vector
        context = torch.sum(attn_weights * lstm_out, dim=1) # (batch, hidden_dim)
        
        # Multi-horizon predictions
        pred_10s = self.head_10s(context)
        pred_30s = self.head_30s(context)
        pred_1m = self.head_1m(context)
        pred_5m = self.head_5m(context)
        
        return {
            '10s': pred_10s,
            '30s': pred_30s,
            '1m': pred_1m,
            '5m': pred_5m,
            'attention': attn_weights.squeeze(-1)
        }
        
    def enable_mc_dropout(self):
        """Enable dropout during inference for uncertainty estimation."""
        for m in self.modules():
            if m.__class__.__name__.startswith('Dropout'):
                m.train()
        # PyTorch LSTM dropout is internal, not a child Dropout module.
        if self.lstm.num_layers > 1:
            self.lstm.train()

    def predict_with_uncertainty(self, x: torch.Tensor, num_samples: int = 10):
        if num_samples < 1:
            raise ValueError("num_samples must be positive")
        self.eval()
        self.enable_mc_dropout()
        
        preds = {'10s': [], '30s': [], '1m': [], '5m': []}
        
        with torch.no_grad():
            for _ in range(num_samples):
                out = self(x)
                for k in preds.keys():
                    preds[k].append(F.softmax(out[k], dim=-1).unsqueeze(0))
                    
        # Calculate mean and variance
        results = {}
        for k in preds.keys():
            stacked = torch.cat(preds[k], dim=0) # (samples, batch, classes)
            mean = torch.mean(stacked, dim=0)
            variance = torch.var(stacked, dim=0, unbiased=False)
            results[k] = {'mean': mean, 'variance': variance}
            
        self.eval() # restore eval mode
        return results

    def save(self, filepath: str):
        torch.save({
            'state_dict': self.state_dict(),
            'input_dim': self.input_dim,
            'num_classes': self.num_classes,
            'hidden_dim': self.hidden_dim, 'num_layers': self.num_layers
        }, filepath)

    @classmethod
    def load(cls, filepath: str):
        data = torch.load(filepath, map_location='cpu', weights_only=True)
        model = cls(input_dim=data['input_dim'], num_classes=data['num_classes'],
                    hidden_dim=data.get('hidden_dim', 256), num_layers=data.get('num_layers', 2))
        model.load_state_dict(data['state_dict'])
        model.eval()
        return model
