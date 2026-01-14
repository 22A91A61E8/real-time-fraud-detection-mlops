import pytest
from unittest.mock import Mock, patch
import numpy as np
from src.prediction import FraudPredictor
from src.model_training import ModelTrainer

class TestFraudPredictor:
    @pytest.fixture
    def predictor(self):
        predictor = FraudPredictor(model_path='models/test.pkl')
        predictor.model_trainer = Mock(spec=ModelTrainer)
        return predictor
    
    def test_predict_fraud(self, predictor):
        predictor.model_trainer.predict_proba = Mock(return_value=np.array([0.8]))
        is_fraud, prob = predictor.predict({'transaction_id': '123', 'amount': 100}, {})
        assert is_fraud == 1
        assert prob == 0.8
    
    def test_predict_legitimate(self, predictor):
        predictor.model_trainer.predict_proba = Mock(return_value=np.array([0.2]))
        is_fraud, prob = predictor.predict({'transaction_id': '124', 'amount': 50}, {})
        assert is_fraud == 0
        assert prob == 0.2
    
    def test_batch_predict(self, predictor):
        predictor.model_trainer.predict_proba = Mock(side_effect=[np.array([0.8]), np.array([0.3])])
        results = predictor.batch_predict(
            [{'transaction_id': '1', 'amount': 100}, {'transaction_id': '2', 'amount': 50}],
            [{}, {}]
        )
        assert len(results) == 2
        assert results[0]['is_fraud'] == 1
        assert results[1]['is_fraud'] == 0
    
    def test_set_threshold(self, predictor):
        predictor.set_threshold(0.7)
        assert predictor.prediction_threshold == 0.7
    
    def test_invalid_threshold(self, predictor):
        with pytest.raises(ValueError):
            predictor.set_threshold(1.5)
    
    def test_cache_prediction(self, predictor):
        predictor._cache_prediction('txn1', 1, 0.9)
        assert 'txn1' in predictor.prediction_cache
        assert predictor.prediction_cache['txn1']['is_fraud'] == 1
