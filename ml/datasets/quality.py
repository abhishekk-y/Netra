import pandas as pd
import numpy as np
from typing import Dict, Any

class DatasetQualityAnalyzer:
    """Analyzes dataset quality and data leakage."""

    def analyze(self, df: pd.DataFrame, label_col: str = 'label', time_col: str = 'timestamp') -> Dict[str, Any]:
        report = {}
        
        # 1. Class Imbalance
        if label_col in df.columns:
            class_counts = df[label_col].value_counts().to_dict()
            report['class_distribution'] = class_counts
            total = len(df)
            report['class_imbalance_ratio'] = {k: v/total for k, v in class_counts.items()}
            
        # 2. NaN/Inf Checks
        null_counts = df.isnull().sum()
        report['missing_values'] = null_counts[null_counts > 0].to_dict()
        
        numeric_df = df.select_dtypes(include=[np.number])
        inf_counts = np.isinf(numeric_df).sum()
        report['inf_values'] = inf_counts[inf_counts > 0].to_dict()
        
        # 3. Duplicates
        duplicates = df.duplicated().sum()
        report['duplicate_rows'] = int(duplicates)
        
        # 4. Leakage checks (highly correlated IP/timestamp to label)
        # Placeholder for complex leakage logic: just checking correlation if label is numeric
        if label_col in df.columns and pd.api.types.is_numeric_dtype(df[label_col]):
            corrs = numeric_df.corrwith(df[label_col]).abs()
            high_corr = corrs.drop(labels=[label_col], errors='ignore')[corrs.drop(labels=[label_col], errors='ignore') > 0.95].to_dict()
            report['potential_leakage_features'] = high_corr
            
        # 5. Temporal Splitting Check
        if time_col in df.columns:
            report['time_range'] = (str(df[time_col].min()), str(df[time_col].max()))
            
        return report

    def temporal_split(self, df: pd.DataFrame, time_col: str, test_ratio: float = 0.2):
        """Perform a strict temporal split. No random splitting for time-series."""
        if time_col not in df.columns:
            raise ValueError(f"Time column {time_col} not found for temporal split.")
        if not 0 < test_ratio < 1 or len(df) < 2:
            raise ValueError("Temporal split needs at least two rows and a test ratio in (0, 1)")
        if df[time_col].isna().any():
            raise ValueError("Temporal split requires non-missing timestamps")
            
        df_sorted = df.sort_values(by=time_col).reset_index(drop=True)
        split_idx = int(len(df_sorted) * (1 - test_ratio))
        split_idx = max(1, min(split_idx, len(df_sorted) - 1))
        boundary = df_sorted.iloc[split_idx][time_col]
        # All observations from a timestamp belong to the same partition.
        split_idx = int((df_sorted[time_col] < boundary).sum())
        if split_idx == 0:
            raise ValueError("Not enough distinct timestamps for a strict temporal split")
        
        train_df = df_sorted.iloc[:split_idx]
        test_df = df_sorted.iloc[split_idx:]
        
        return train_df, test_df
