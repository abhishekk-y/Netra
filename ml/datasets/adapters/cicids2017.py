import pandas as pd
import numpy as np
from typing import Dict, Any

class CICIDS2017Adapter:
    """Adapter for CIC-IDS2017 Dataset."""
    
    # Mapping original labels to unified attack taxonomy
    LABEL_MAP = {
        'BENIGN': 'BENIGN',
        'FTP-Patator': 'CREDENTIAL_ACCESS',
        'SSH-Patator': 'CREDENTIAL_ACCESS',
        'DoS slowloris': 'IMPACT',
        'DoS Slowhttptest': 'IMPACT',
        'DoS Hulk': 'IMPACT',
        'DoS GoldenEye': 'IMPACT',
        'Heartbleed': 'INITIAL_ACCESS',
        'Web Attack  Brute Force': 'CREDENTIAL_ACCESS',
        'Web Attack  XSS': 'INITIAL_ACCESS',
        'Web Attack  Sql Injection': 'INITIAL_ACCESS',
        'Infiltration': 'LATERAL_MOVEMENT',
        'Bot': 'COMMAND_AND_CONTROL',
        'PortScan': 'RECONNAISSANCE',
        'DDoS': 'IMPACT'
    }

    def __init__(self):
        pass
        
    def load(self, filepath: str) -> pd.DataFrame:
        """Load CSV and standardize columns and labels."""
        df = pd.read_csv(filepath)
        
        # Clean column names (strip whitespace)
        df.columns = [c.strip() for c in df.columns]
        
        # Map labels
        if 'Label' in df.columns:
            df['unified_label'] = df['Label'].map(self.LABEL_MAP).fillna('UNKNOWN')
            
        # Clean Inf/NaN
        df.replace([np.inf, -np.inf], np.nan, inplace=True)
        df.fillna(0, inplace=True)
        
        return df

    def to_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Map CIC-IDS columns to our standardized feature schema."""
        features = pd.DataFrame()
        
        # We perform best-effort mapping to our FlowFeatureExtractor schema.
        if 'Flow Duration' in df.columns:
            features['duration_ms'] = df['Flow Duration'] / 1000.0
            
        if 'Total Fwd Packets' in df.columns:
            features['fwd_packets'] = df['Total Fwd Packets']
            features['bwd_packets'] = df['Total Backward Packets']
            features['total_packets'] = features['fwd_packets'] + features['bwd_packets']
            
        if 'Total Length of Fwd Packets' in df.columns:
            features['fwd_bytes'] = df['Total Length of Fwd Packets']
            features['bwd_bytes'] = df['Total Length of Bwd Packets']
            features['total_bytes'] = features['fwd_bytes'] + features['bwd_bytes']
            
        if 'Protocol' in df.columns:
            features['protocol_encoded'] = df['Protocol']
            
        # Add labels if present
        if 'unified_label' in df.columns:
            features['label'] = df['unified_label']
            
        return features
