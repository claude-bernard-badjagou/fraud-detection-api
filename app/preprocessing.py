import numpy as np
import pandas as pd
import json
from pathlib import Path

MODEL_DIR = Path(__file__).parent.parent / "model"

with open(MODEL_DIR / "feature_cols.json", "r") as f:
    FEATURE_COLS = json.load(f)

def preprocess_transaction(data: dict) -> np.ndarray:
    """Transforme un dict de transaction en array pret pour prediction."""
    
    row = {col: -999 for col in FEATURE_COLS}
    
    for key, value in data.items():
        if key in row:
            row[key] = value

    # Features ajoutees
    c1 = data.get('C1', -999)
    c13 = data.get('C13', -999)
    c14 = data.get('C14', -999)
    d1 = data.get('D1', -999)
    d15 = data.get('D15', -999)
    amt = data.get('TransactionAmt', -999)

    row['C1_C14_ratio'] = c1 / (c14 + 0.01) if 'C1_C14_ratio' in row else -999
    row['C1_C13_ratio'] = c1 / (c13 + 0.01) if 'C1_C13_ratio' in row else -999
    row['D1_D15_diff']  = d1 - d15 if 'D1_D15_diff' in row else -999
    row['amt_cents']    = (amt * 100) % 100 if 'amt_cents' in row else -999

    values = [row[col] for col in FEATURE_COLS]
    return np.array([values], dtype=np.float32)