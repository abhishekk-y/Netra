import torch
import torch.nn as nn
import numpy as np

class TemperatureScaler(nn.Module):
    """Temperature scaling for model calibration."""
    
    def __init__(self):
        super(TemperatureScaler, self).__init__()
        self.temperature = nn.Parameter(torch.ones(1) * 1.5)
        
    def forward(self, logits: torch.Tensor) -> torch.Tensor:
        return logits / self.temperature

def platt_scale(preds, labels):
    """Platt scaling (logistic regression on outputs)."""
    from sklearn.linear_model import LogisticRegression
    lr = LogisticRegression()
    lr.fit(preds.reshape(-1, 1), labels)
    return lr

def compute_reliability_diagram(y_true: np.ndarray, y_prob: np.ndarray, n_bins: int = 10):
    confidences = np.max(y_prob, axis=1)
    predictions = np.argmax(y_prob, axis=1)
    accuracies = predictions == y_true
    
    bins = np.linspace(0, 1, n_bins + 1)
    bin_accs = []
    bin_confs = []
    
    for i in range(n_bins):
        bin_lower = bins[i]
        bin_upper = bins[i+1]
        in_bin = (confidences > bin_lower) & (confidences <= bin_upper)
        
        if np.any(in_bin):
            bin_accs.append(np.mean(accuracies[in_bin]))
            bin_confs.append(np.mean(confidences[in_bin]))
        else:
            bin_accs.append(0)
            bin_confs.append(0)
            
    return {"accuracies": bin_accs, "confidences": bin_confs}
