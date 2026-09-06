import pandas as pd
import numpy as np

class UNSWNB15Adapter:
    """Adapter for UNSW-NB15 Dataset."""
    
    LABEL_MAP = {
        'Normal': 'BENIGN',
        'Generic': 'IMPACT', # Simplified mapping
        'Exploits': 'INITIAL_ACCESS',
        'Fuzzers': 'RECONNAISSANCE',
        'DoS': 'IMPACT',
        'Reconnaissance': 'RECONNAISSANCE',
        'Analysis': 'RECONNAISSANCE',
        'Backdoor': 'COMMAND_AND_CONTROL',
        'Shellcode': 'EXECUTION',
        'Worms': 'LATERAL_MOVEMENT'
    }

    def load(self, filepath: str) -> pd.DataFrame:
        df = pd.read_csv(filepath)
        df.columns = [c.strip() for c in df.columns]
        
        # UNSW uses 'attack_cat' for attack category
        if 'attack_cat' in df.columns:
            df['attack_cat'] = df['attack_cat'].str.strip()
            # Map empty or NaN to Normal
            df['attack_cat'].fillna('Normal', inplace=True)
            df.loc[df['attack_cat'] == '', 'attack_cat'] = 'Normal'
            df['unified_label'] = df['attack_cat'].map(self.LABEL_MAP).fillna('UNKNOWN')
            
        df.replace([np.inf, -np.inf], np.nan, inplace=True)
        df.fillna(0, inplace=True)
        return df
