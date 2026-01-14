"""Real-time Fraud Prediction Module"""
import logging
from typing import Dict, Tuple
import numpy as np
from src.feature_engineering import FeatureEngineering
from src.model_training import ModelTrainer

logger = logging.getLogger(__name__)

class FraudPredictor:
    """Real-time fraud prediction service"""
    
    def __init__(self, model_path: str, scaler_path: str = None):
        self.model_trainer = ModelTrainer()
        self.model_trainer.load_model(model_path)
        self.feature_engineer = FeatureEngineering(scaler_path)
        self.prediction_threshold = 0.5
        self.prediction_cache = {}
    
    def predict(self, transaction: Dict, customer_history: Dict) -> Tuple[int, float]:
        """Predict if transaction is fraudulent"""
        try:
            features = self.feature_engineer.create_feature_vector(transaction, customer_history)
            normalized_features = self.feature_engineer.normalize_features(features)
            
            fraud_probability = self.model_trainer.predict_proba(normalized_features)[0]
            is_fraud = 1 if fraud_probability >= self.prediction_threshold else 0
            
            # Cache prediction
            self._cache_prediction(transaction['transaction_id'], is_fraud, fraud_probability)
            
            logger.info(f"Prediction: {is_fraud}, Probability: {fraud_probability:.4f}")
            return is_fraud, fraud_probability
        
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return 0, 0.0
    
    def batch_predict(self, transactions: list, customer_histories: list) -> list:
        """Batch predict multiple transactions"""
        predictions = []
        for txn, history in zip(transactions, customer_histories):
            is_fraud, prob = self.predict(txn, history)
            predictions.append({'is_fraud': is_fraud, 'probability': prob})
        return predictions
    
    def set_threshold(self, threshold: float):
        """Set fraud detection threshold"""
        if 0 <= threshold <= 1:
            self.prediction_threshold = threshold
            logger.info(f"Threshold set to {threshold}")
        else:
            raise ValueError(f"Threshold must be between 0 and 1")
    
    def _cache_prediction(self, txn_id: str, is_fraud: int, probability: float):
        """Cache prediction result"""
        self.prediction_cache[txn_id] = {'is_fraud': is_fraud, 'probability': probability}
        if len(self.prediction_cache) > 10000:
            self.prediction_cache.popitem()

if __name__ == "__main__":
    logger.info("Fraud prediction module initialized")
