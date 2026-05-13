import json
import os
from datetime import datetime
from pathlib import Path

# =============================================================================
# STRATEGIE : PostgreSQL en production, fichier JSON en local
# =============================================================================
DATABASE_URL = os.getenv("DATABASE_URL", None)

# --- Fallback local JSON ---
LOG_DIR  = Path(__file__).parent.parent / "logs"
LOG_FILE = LOG_DIR / "predictions.json"
LOG_DIR.mkdir(exist_ok=True)


def _get_db_conn():
    """Retourne une connexion PostgreSQL si DATABASE_URL est defini."""
    if DATABASE_URL:
        import psycopg2
        return psycopg2.connect(DATABASE_URL)
    return None


def _init_db():
    """Cree la table si elle n'existe pas."""
    conn = _get_db_conn()
    if conn is None:
        return
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS predictions (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMPTZ DEFAULT NOW(),
                    transaction_amt FLOAT,
                    fraud_probability FLOAT,
                    is_fraud BOOLEAN,
                    risk_level VARCHAR(10),
                    threshold FLOAT,
                    inputs JSONB
                )
            """)
        conn.commit()
    finally:
        conn.close()


# Initialiser la table au demarrage
_init_db()


def log_prediction(inputs: dict, result: dict):
    """Enregistre une prediction - PostgreSQL ou JSON selon l'environnement."""
    conn = _get_db_conn()

    if conn:
        # --- Mode PostgreSQL ---
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO predictions
                    (transaction_amt, fraud_probability, is_fraud, risk_level, threshold, inputs)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    inputs.get("TransactionAmt", 0),
                    result["fraud_probability"],
                    result["is_fraud"],
                    result["risk_level"],
                    result["threshold"],
                    json.dumps(inputs)
                ))
            conn.commit()
        finally:
            conn.close()
    else:
        # --- Mode fichier JSON local ---
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
    """Charge les logs - PostgreSQL ou fichier JSON selon l'environnement."""
    conn = _get_db_conn()

    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT timestamp, transaction_amt, fraud_probability,
                           is_fraud, risk_level, threshold, inputs
                    FROM predictions
                    ORDER BY timestamp DESC
                    LIMIT 1000
                """)
                rows = cur.fetchall()
            entries = []
            for row in rows:
                entries.append({
                    "timestamp":         row[0].isoformat() if row[0] else "",
                    "transaction_amt":   row[1],
                    "fraud_probability": row[2],
                    "is_fraud":          row[3],
                    "risk_level":        row[4],
                    "threshold":         row[5],
                    "inputs":            row[6]
                })
            return entries
        finally:
            conn.close()
    else:
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

    probas      = [e["fraud_probability"] for e in entries]
    is_fraud    = [e["is_fraud"]          for e in entries]
    risk_levels = [e["risk_level"]        for e in entries]

    return {
        "total":       len(entries),
        "fraud_count": sum(is_fraud),
        "fraud_rate":  sum(is_fraud) / len(is_fraud),
        "proba_mean":  sum(probas) / len(probas),
        "proba_min":   min(probas),
        "proba_max":   max(probas),
        "risk_counts": {
            "CRITICAL": risk_levels.count("CRITICAL"),
            "HIGH":     risk_levels.count("HIGH"),
            "MEDIUM":   risk_levels.count("MEDIUM"),
            "LOW":      risk_levels.count("LOW"),
        }
    }