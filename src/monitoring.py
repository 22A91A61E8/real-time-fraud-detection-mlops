"""Monitoring and Alerting Module"""
import logging
from typing import Dict
from datetime import datetime
from prometheus_client import Counter, Histogram, Gauge
from collections import defaultdict

logger = logging.getLogger(__name__)

# Prometheus metrics
predictions_total = Counter('fraud_predictions_total', 'Total predictions', ['prediction_type'])
prediction_latency = Histogram('fraud_prediction_latency_ms', 'Prediction latency')
fraud_detection_rate = Gauge('fraud_detection_rate', 'Current fraud detection rate')
api_errors_total = Counter('fraud_api_errors_total', 'Total API errors')

class MetricsCollector:
    """Collect and manage system metrics"""
    
    def __init__(self):
        self.predictions = defaultdict(int)
        self.fraud_detections = 0
        self.total_predictions = 0
        self.latencies = []
        self.error_count = 0
    
    def record_prediction(self, is_fraud: int, probability: float):
        """Record a prediction"""
        self.total_predictions += 1
        pred_type = 'fraud' if is_fraud == 1 else 'legitimate'
        self.predictions[pred_type] += 1
        
        if is_fraud == 1:
            self.fraud_detections += 1
        
        predictions_total.labels(prediction_type=pred_type).inc()
    
    def record_latency(self, latency_ms: float):
        """Record prediction latency"""
        self.latencies.append(latency_ms)
        prediction_latency.observe(latency_ms)
    
    def record_error(self):
        """Record API error"""
        self.error_count += 1
        api_errors_total.inc()
    
    def get_metrics(self) -> Dict:
        """Get current metrics"""
        detection_rate = (self.fraud_detections / max(self.total_predictions, 1)) * 100
        fraud_detection_rate.set(detection_rate)
        
        avg_latency = sum(self.latencies[-100:]) / max(len(self.latencies[-100:]), 1)
        
        return {
            'total_predictions': self.total_predictions,
            'fraud_detections': self.fraud_detections,
            'fraud_detection_rate': f"{detection_rate:.2f}%",
            'legitimate_predictions': self.predictions['legitimate'],
            'average_latency_ms': f"{avg_latency:.2f}",
            'total_errors': self.error_count,
            'timestamp': datetime.now().isoformat()
        }

class AlertingService:
    """Generate alerts for anomalies"""
    
    def __init__(self, fraud_rate_threshold: float = 5.0):
        self.fraud_rate_threshold = fraud_rate_threshold
        self.alerts = []
    
    def check_fraud_rate(self, metrics: Dict) -> bool:
        """Check if fraud rate exceeds threshold"""
        fraud_rate = float(metrics['fraud_detection_rate'].rstrip('%'))
        if fraud_rate > self.fraud_rate_threshold:
            alert = {
                'type': 'HIGH_FRAUD_RATE',
                'value': fraud_rate,
                'threshold': self.fraud_rate_threshold,
                'timestamp': datetime.now().isoformat()
            }
            self.alerts.append(alert)
            logger.warning(f"Alert: High fraud rate detected: {fraud_rate}%")
            return True
        return False
    
    def get_alerts(self):
        """Get current alerts"""
        return self.alerts[-100:]

if __name__ == "__main__":
    logger.info("Monitoring module initialized")
