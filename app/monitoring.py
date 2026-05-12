import json
import os
from datetime import datetime
from pathlib import Path

LOG_DIR  = Path(__file__).parent.parent / "logs"
LOG_FILE = LOG_DIR / "predictions.json"

LOG_DIR.mkdir(exist_ok=True)

def log_prediction(inputs: dict, result: dict):
    """Enregistre chaque prediction avec ses inputs et outputs."""
    entry = {
        "timestamp":         datetime.now().isoformat(),
        "inputs":            inputs,
        "fraud_probability": result["fraud_probability"],
        "is_fraud":          result["is_fraud"],
        "risk_level":        result["risk_level"],
        "threshold":         result["threshold"]
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def load_logs() -> list:
    """Charge tous les logs de predictions."""
    if not LOG_FILE.exists():
        return []
    entries = []
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except Exception:
                    continue
    return entries


def compute_stats(entries: list) -> dict:
    """Calcule les statistiques de monitoring."""
    if not entries:
        return {}

    probas     = [e["fraud_probability"] for e in entries]
    is_fraud   = [e["is_fraud"] for e in entries]
    risk_levels = [e["risk_level"] for e in entries]

    return {
        "total":           len(entries),
        "fraud_count":     sum(is_fraud),
        "fraud_rate":      sum(is_fraud) / len(is_fraud),
        "proba_mean":      sum(probas) / len(probas),
        "proba_min":       min(probas),
        "proba_max":       max(probas),
        "risk_counts": {
            "CRITICAL": risk_levels.count("CRITICAL"),
            "HIGH":     risk_levels.count("HIGH"),
            "MEDIUM":   risk_levels.count("MEDIUM"),
            "LOW":      risk_levels.count("LOW"),
        }
    }