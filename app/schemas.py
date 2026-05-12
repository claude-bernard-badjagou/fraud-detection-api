from pydantic import BaseModel, ConfigDict
from typing import List, Optional

class TransactionInput(BaseModel):
    TransactionAmt: float
    ProductCD: int
    card1: float = -999
    card2: float = -999
    card3: float = -999
    card4: int = -999
    card5: float = -999
    card6: int = -999
    addr1: float = -999
    addr2: float = -999
    dist1: float = -999
    P_emaildomain: int = -999
    R_emaildomain: int = -999
    C1: float = -999
    C2: float = -999
    C3: float = -999
    C4: float = -999
    C5: float = -999
    C6: float = -999
    C7: float = -999
    C8: float = -999
    C9: float = -999
    C10: float = -999
    C11: float = -999
    C12: float = -999
    C13: float = -999
    C14: float = -999
    D1: float = -999
    D2: float = -999
    D3: float = -999
    D4: float = -999
    D5: float = -999
    D8: float = -999
    D9: float = -999
    D10: float = -999
    D11: float = -999
    D15: float = -999
    M1: int = -999
    M2: int = -999
    M3: int = -999
    M4: int = -999
    M5: int = -999
    M6: int = -999
    M7: int = -999
    M8: int = -999
    M9: int = -999
    V91: float = -999
    V70: float = -999
    V283: float = -999
    V287: float = -999
    V312: float = -999
    V90: float = -999
    V281: float = -999
    V69: float = -999

    model_config = ConfigDict(
        protected_namespaces=(),
        json_schema_extra={
            "example": {
                "TransactionAmt": 75.0,
                "ProductCD": 1,
                "card1": 4000,
                "C1": 1.0,
                "C13": 1.0,
                "C14": 1.0,
                "D1": 14.0,
                "D15": 300.0
            }
        }
    )

class PredictionOutput(BaseModel):
    fraud_probability: float
    is_fraud: bool
    threshold: float
    risk_level: str

class BatchInput(BaseModel):
    transactions: List[TransactionInput]

class BatchOutput(BaseModel):
    predictions: List[PredictionOutput]
    count: int

class HealthResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    status: str
    model_version: str
    n_features: int

class ModelInfoResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    model_type: str
    version: str
    n_features: int
    n_trees: int
    threshold: float
    metrics: dict