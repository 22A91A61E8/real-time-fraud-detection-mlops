"""FastAPI Application for Fraud Detection"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import logging
from src.config import settings
from src.prediction import FraudPredictor
from src.monitoring import MetricsCollector

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug
)

metrics_collector = MetricsCollector()
fraud_predictor = None

class Transaction(BaseModel):
    """Transaction data model"""
    transaction_id: str
    customer_id: str
    amount: float
    merchant_id: str
    timestamp: str
    location: str
    device_id: str
    transaction_type: str
    card_present: bool

class CustomerHistory(BaseModel):
    """Customer history model"""
    amounts: Optional[List[float]] = []
    txn_1h: int = 0
    txn_24h: int = 0

class PredictionResponse(BaseModel):
    """Prediction response model"""
    transaction_id: str
    is_fraud: int
    fraud_probability: float
    processing_time_ms: float

@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    global fraud_predictor
    fraud_predictor = FraudPredictor(
        model_path=settings.model_path,
        scaler_path=settings.scaler_path
    )
    logger.info("API started successfully")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/predict")
async def predict(transaction: Transaction, customer_history: CustomerHistory):
    """Predict fraud for single transaction"""
    try:
        import time
        start_time = time.time()
        
        is_fraud, probability = fraud_predictor.predict(
            transaction.dict(),
            customer_history.dict()
        )
        
        processing_time = (time.time() - start_time) * 1000
        
        metrics_collector.record_prediction(is_fraud, probability)
        
        return PredictionResponse(
            transaction_id=transaction.transaction_id,
            is_fraud=is_fraud,
            fraud_probability=probability,
            processing_time_ms=processing_time
        )
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/batch_predict")
async def batch_predict(transactions: List[Transaction], customer_histories: List[CustomerHistory]):
    """Batch predict multiple transactions"""
    try:
        results = []
        for txn, history in zip(transactions, customer_histories):
            response = await predict(txn, history)
            results.append(response)
        return {"predictions": results}
    except Exception as e:
        logger.error(f"Batch prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics")
async def get_metrics():
    """Get system metrics"""
    return metrics_collector.get_metrics()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.api_host, port=settings.api_port, workers=settings.api_workers)
