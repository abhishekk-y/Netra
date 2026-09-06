import numpy as np
from sklearn.metrics import roc_auc_score, precision_recall_curve, auc

class ForecastMetrics:
    """Calculation of forecasting and sequence metrics."""
    
    @staticmethod
    def expected_calibration_error(y_true: np.ndarray, y_prob: np.ndarray, n_bins: int = 10) -> float:
        """Calculate ECE for a binary or multiclass setup."""
        # Simple binary approximation
        confidences = np.max(y_prob, axis=1)
        predictions = np.argmax(y_prob, axis=1)
        accuracies = predictions == y_true
        
        bins = np.linspace(0, 1, n_bins + 1)
        ece = 0.0
        
        for i in range(n_bins):
            bin_lower = bins[i]
            bin_upper = bins[i+1]
            in_bin = (confidences > bin_lower) & (confidences <= bin_upper)
            prop_in_bin = np.mean(in_bin)
            
            if prop_in_bin > 0:
                accuracy_in_bin = np.mean(accuracies[in_bin])
                avg_confidence_in_bin = np.mean(confidences[in_bin])
                ece += np.abs(avg_confidence_in_bin - accuracy_in_bin) * prop_in_bin
                
        return float(ece)
        
    @staticmethod
    def forecast_lead_time(predicted_times: np.ndarray, actual_times: np.ndarray) -> float:
        """Calculate how far ahead predictions were correct."""
        diffs = actual_times - predicted_times
        valid = diffs[diffs > 0]
        if len(valid) == 0: return 0.0
        return float(np.mean(valid))
