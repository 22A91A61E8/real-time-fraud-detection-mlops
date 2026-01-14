"""Feature Engineering for Fraud Detection"""
import logging
from typing import Dict, List
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import joblib

logger = logging.getLogger(__name__)

class FeatureEngineering:
    """Feature engineering module for fraud detection"""
    
    def __init__(self, scaler_path: str = None):
        self.scaler = StandardScaler()
        self.scaler_path = scaler_path
        if scaler_path:
            self.scaler = joblib.load(scaler_path)
    
    def extract_temporal_features(self, timestamp: str) -> Dict:
        """Extract temporal features from transaction timestamp"""
        dt = datetime.fromisoformat(timestamp)
        return {
            'hour': dt.hour,
            'day_of_week': dt.weekday(),
            'is_weekend': 1 if dt.weekday() >= 5 else 0,
            'is_night': 1 if dt.hour >= 22 or dt.hour <= 5 else 0,
            'day_of_month': dt.day
        }
    
    def extract_amount_features(self, amount: float, customer_history: List[float]) -> Dict:
        """Extract amount-based features"""
        if not customer_history:
            customer_history = [amount]
        
        return {
            'amount': amount,
            'amount_log': np.log1p(amount),
            'amount_normalized': amount / (np.mean(customer_history) + 1e-5),
            'amount_deviation': abs(amount - np.mean(customer_history)) / (np.std(customer_history) + 1e-5)
        }
    
    def extract_frequency_features(self, customer_id: str, transactions_1h: int, transactions_24h: int) -> Dict:
        """Extract frequency features"""
        return {
            'transactions_1h': transactions_1h,
            'transactions_24h': transactions_24h,
            'avg_txn_per_hour': transactions_24h / 24
        }
    
    def create_feature_vector(self, transaction: Dict, customer_history: Dict) -> Dict:
        """Create complete feature vector for model prediction"""
        features = {}
        
        # Temporal features
        temporal_feat = self.extract_temporal_features(transaction['timestamp'])
        features.update(temporal_feat)
        
        # Amount features
        amount_feat = self.extract_amount_features(
            transaction['amount'],
            customer_history.get('amounts', [])
        )
        features.update(amount_feat)
        
        # Frequency features
        freq_feat = self.extract_frequency_features(
            transaction['customer_id'],
            customer_history.get('txn_1h', 0),
            customer_history.get('txn_24h', 0)
        )
        features.update(freq_feat)
        
        # Additional features
        features['card_present'] = transaction.get('card_present', 0)
        features['transaction_type_encoded'] = self._encode_transaction_type(transaction.get('transaction_type', ''))
        features['location_riskiness'] = self._calculate_location_risk(transaction.get('location', ''))
        
        return features
    
    def _encode_transaction_type(self, tx_type: str) -> int:
        """Encode transaction type"""
        type_mapping = {'online': 1, 'atm': 2, 'pos': 3, 'transfer': 4}
        return type_mapping.get(tx_type.lower(), 0)
    
    def _calculate_location_risk(self, location: str) -> float:
        """Calculate location risk score"""
        high_risk_locations = ['high_risk_country', 'suspicious_region']
        return 1.0 if location in high_risk_locations else 0.0
    
    def normalize_features(self, features: Dict) -> np.ndarray:
        """Normalize features using scaler"""
        feature_list = [
            features.get('amount', 0),
            features.get('amount_log', 0),
            features.get('transactions_1h', 0),
            features.get('transactions_24h', 0),
            features.get('card_present', 0),
            features.get('hour', 0),
            features.get('is_weekend', 0),
            features.get('amount_deviation', 0)
        ]
        return self.scaler.transform([feature_list])
    
    def save_scaler(self, path: str):
        """Save scaler to disk"""
        joblib.dump(self.scaler, path)
        logger.info(f"Scaler saved to {path}")

if __name__ == "__main__":
    fe = FeatureEngineering()
    sample_transaction = {
        'transaction_id': '123',
        'customer_id': 'C001',
        'amount': 100.50,
        'timestamp': datetime.now().isoformat(),
        'card_present': 1,
        'location': 'US',
        'transaction_type': 'pos'
    }
    sample_history = {'amounts': [50, 75, 120], 'txn_1h': 2, 'txn_24h': 15}
    features = fe.create_feature_vector(sample_transaction, sample_history)
    print("Features:", features)
