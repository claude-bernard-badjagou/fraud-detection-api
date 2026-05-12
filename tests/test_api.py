from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"

def test_model_info():
    r = client.get("/model/info")
    assert r.status_code == 200
    assert "n_trees" in r.json()

def test_predict_single():
    payload = {
        "TransactionAmt": 75.0,
        "ProductCD": 1,
        "card1": 4000,
        "C1": 1.0,
        "C13": 1.0,
        "C14": 1.0,
        "D1": 14.0,
        "D15": 300.0
    }
    r = client.post("/predict", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert "fraud_probability" in data
    assert "is_fraud" in data
    assert "risk_level" in data

def test_predict_batch():
    payload = {
        "transactions": [
            {"TransactionAmt": 75.0, "ProductCD": 1},
            {"TransactionAmt": 500.0, "ProductCD": 3}
        ]
    }
    r = client.post("/predict/batch", json=payload)
    assert r.status_code == 200
    assert r.json()["count"] == 2