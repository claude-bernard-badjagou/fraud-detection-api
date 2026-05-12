from fastapi import FastAPI, HTTPException
from .schemas import (
    TransactionInput, PredictionOutput,
    BatchInput, BatchOutput,
    HealthResponse, ModelInfoResponse
)
from .model import predict_single, predict_batch, get_model_info
from .monitoring import load_logs, compute_stats

app = FastAPI(
    title="Fraud Detection API",
    description="API de detection de fraude - IEEE-CIS",
    version="1.0.0"
)

@app.get("/health", response_model=HealthResponse)
def health():
    info = get_model_info()
    return HealthResponse(
        status="healthy",
        model_version=info["version"],
        n_features=info["n_features"]
    )

@app.get("/model/info", response_model=ModelInfoResponse)
def model_info():
    return get_model_info()

@app.get("/monitoring/stats")
def monitoring_stats():
    entries = load_logs()
    return compute_stats(entries)

@app.post("/predict", response_model=PredictionOutput)
def predict(transaction: TransactionInput):
    try:
        data = transaction.model_dump()
        result = predict_single(data)
        return PredictionOutput(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict/batch", response_model=BatchOutput)
def predict_batch_endpoint(batch: BatchInput):
    try:
        data_list = [t.model_dump() for t in batch.transactions]
        results = predict_batch(data_list)
        return BatchOutput(
            predictions=[PredictionOutput(**r) for r in results],
            count=len(results)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))