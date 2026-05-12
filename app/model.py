import xgboost as xgb
import numpy as np
import json
import joblib
from pathlib import Path
from .preprocessing import preprocess_transaction, FEATURE_COLS
from .monitoring import log_prediction

MODEL_DIR = Path(__file__).parent.parent / "model"

# Charger au demarrage
_booster = xgb.Booster()
_booster.load_model(str(MODEL_DIR / "model.json"))

_threshold = joblib.load(MODEL_DIR / "threshold.joblib")

with open(MODEL_DIR / "model_config.json", "r") as f:
    _config = json.load(f)

def predict_single(data: dict) -> dict:
    features = preprocess_transaction(data)
    dmatrix  = xgb.DMatrix(features, feature_names=FEATURE_COLS)
    proba    = float(_booster.predict(dmatrix)[0])
    is_fraud = proba >= _threshold

    if proba >= 0.9:
        risk = "CRITICAL"
    elif proba >= _threshold:
        risk = "HIGH"
    elif proba >= 0.3:
        risk = "MEDIUM"
    else:
        risk = "LOW"

    result = {
        "fraud_probability": round(proba, 4),
        "is_fraud":          is_fraud,
        "threshold":         _threshold,
        "risk_level":        risk
    }

    # Logger chaque prediction
    log_prediction(data, result)

    return result

def predict_batch(transactions: list) -> list:
    """Prediction pour un batch."""
    all_features = []
    for txn in transactions:
        all_features.append(preprocess_transaction(txn)[0])
    
    features_array = np.array(all_features, dtype=np.float32)
    dmatrix = xgb.DMatrix(features_array, feature_names=FEATURE_COLS)
    probas = _booster.predict(dmatrix)
    
    results = []
    for proba in probas:
        proba = float(proba)
        is_fraud = proba >= _threshold
        if proba >= 0.9:
            risk = "CRITICAL"
        elif proba >= _threshold:
            risk = "HIGH"
        elif proba >= 0.3:
            risk = "MEDIUM"
        else:
            risk = "LOW"
        results.append({
            "fraud_probability": round(proba, 4),
            "is_fraud": is_fraud,
            "threshold": _threshold,
            "risk_level": risk
        })
    return results

def get_model_info() -> dict:
    return {
        "model_type": _config["model_type"],
        "version": _config["version"],
        "n_features": _config["n_features"],
        "n_trees": _booster.num_boosted_rounds(),
        "threshold": _threshold,
        "metrics": _config["metrics"]
    }