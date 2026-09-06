import math
from typing import List, Tuple, Dict, Any

class StatisticalAnomalyEngine:
    
    def z_score_anomaly(self, value: float, mean: float, std: float) -> float:
        if std == 0:
            return 0.0 if value == mean else 100.0
        z = abs(value - mean) / std
        # Map z-score to 0-100 (e.g. z=3 is 99% anomaly)
        score = (1 - math.exp(-z)) * 100
        return min(100.0, max(0.0, score))
        
    def ewma_anomaly(self, values: List[float], span: int = 20) -> float:
        if not values:
            return 0.0
        
        alpha = 2.0 / (span + 1.0)
        ewma = values[0]
        ewmvar = 0.0
        
        for val in values[1:-1]:
            diff = val - ewma
            ewma = ewma + alpha * diff
            ewmvar = (1 - alpha) * (ewmvar + alpha * diff ** 2)
            
        std = math.sqrt(ewmvar)
        return self.z_score_anomaly(values[-1], ewma, std)
        
    def mad_anomaly(self, value: float, values: List[float]) -> float:
        if not values:
            return 0.0
        median = sorted(values)[len(values) // 2]
        deviations = [abs(v - median) for v in values]
        mad = sorted(deviations)[len(deviations) // 2]
        
        if mad == 0:
            return 0.0 if value == median else 100.0
            
        modified_z = 0.6745 * abs(value - median) / mad
        score = (1 - math.exp(-modified_z / 3)) * 100
        return min(100.0, max(0.0, score))
        
    def entropy_anomaly(self, distribution: Dict[Any, int]) -> float:
        total = sum(distribution.values())
        if total == 0:
            return 0.0
        entropy = 0.0
        for count in distribution.values():
            p = count / total
            if p > 0:
                entropy -= p * math.log2(p)
                
        # Normalize assuming max entropy is log2(len(distribution))
        max_ent = math.log2(len(distribution)) if len(distribution) > 1 else 1
        norm_entropy = entropy / max_ent
        
        # Very low or very high entropy can be anomalous. Here we score based on deviation from expected.
        # Simplistic implementation:
        if norm_entropy < 0.2 or norm_entropy > 0.8:
            return 80.0
        return 20.0
        
    def rate_change_detection(self, values: List[float], threshold: float = 3.0) -> Tuple[bool, float]:
        if len(values) < 2:
            return False, 0.0
        
        current = values[-1]
        previous = sum(values[:-1]) / (len(values) - 1)
        
        if previous == 0:
            return (True, 100.0) if current > 0 else (False, 0.0)
            
        ratio = current / previous
        is_anomalous = ratio > threshold or ratio < (1/threshold)
        
        score = min(100.0, abs(math.log(ratio)) * 20)
        return is_anomalous, score
        
    def analyze_host(self, host_id: str, features: Dict[str, List[float]]) -> Dict[str, Any]:
        results = {}
        total_score = 0.0
        
        for feature_name, values in features.items():
            if not values:
                continue
            
            ewma_score = self.ewma_anomaly(values)
            mad_score = self.mad_anomaly(values[-1], values)
            
            feat_score = max(ewma_score, mad_score)
            results[feature_name] = feat_score
            total_score += feat_score
            
        avg_score = total_score / len(features) if features else 0.0
        return {
            "host_id": host_id,
            "feature_scores": results,
            "combined_score": min(100.0, avg_score * 1.5) # Amplify slightly
        }
