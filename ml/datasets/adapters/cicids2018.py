import pandas as pd
import numpy as np

class CICIDS2018Adapter:
    """Adapter for CSE-CIC-IDS2018 Dataset."""
    
    LABEL_MAP = {
        'Benign': 'BENIGN',
        'FTP-BruteForce': 'CREDENTIAL_ACCESS',
        'SSH-BruteForce': 'CREDENTIAL_ACCESS',
        'DoS-GoldenEye': 'IMPACT',
        'DoS-Slowloris': 'IMPACT',
        'DoS-SlowHTTPTest': 'IMPACT',
        'DoS-Hulk': 'IMPACT',
        'DDoS-LOIC-HTTP': 'IMPACT',
        'DDoS-HOIC': 'IMPACT',
        'Brute Force -Web': 'CREDENTIAL_ACCESS',
        'Brute Force -XSS': 'INITIAL_ACCESS',
        'SQL Injection': 'INITIAL_ACCESS',
        'Infiltration': 'LATERAL_MOVEMENT',
        'Bot': 'COMMAND_AND_CONTROL'
    }

    def load(self, filepath: str) -> pd.DataFrame:
        df = pd.read_csv(filepath)
        df.columns = [c.strip() for c in df.columns]
        if 'Label' in df.columns:
            df['unified_label'] = df['Label'].map(self.LABEL_MAP).fillna('UNKNOWN')
        df.replace([np.inf, -np.inf], np.nan, inplace=True)
        df.fillna(0, inplace=True)
        return df
