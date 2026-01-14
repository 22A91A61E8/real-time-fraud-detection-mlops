"""Utility Functions for Fraud Detection System"""
import logging
from typing import Dict, List
import json
from datetime import datetime
import hashlib
import uuid

logger = logging.getLogger(__name__)

def setup_logging(level: str = 'INFO'):
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def generate_transaction_id() -> str:
    """Generate unique transaction ID"""
    return str(uuid.uuid4())

def hash_value(value: str) -> str:
    """Hash a value for anonymization"""
    return hashlib.sha256(value.encode()).hexdigest()

def validate_transaction_data(transaction: Dict) -> bool:
    """Validate transaction data structure"""
    required_fields = [
        'transaction_id', 'customer_id', 'amount',
        'merchant_id', 'timestamp', 'location',
        'device_id', 'transaction_type', 'card_present'
    ]
    return all(field in transaction for field in required_fields)

def format_timestamp(dt: datetime = None) -> str:
    """Format datetime to ISO format string"""
    if dt is None:
        dt = datetime.now()
    return dt.isoformat()

def parse_timestamp(timestamp_str: str) -> datetime:
    """Parse ISO format timestamp string"""
    return datetime.fromisoformat(timestamp_str)

def batch_data(data: List, batch_size: int) -> List[List]:
    """Split data into batches"""
    batches = []
    for i in range(0, len(data), batch_size):
        batches.append(data[i:i + batch_size])
    return batches

def serialize_prediction(pred_dict: Dict) -> str:
    """Serialize prediction to JSON"""
    return json.dumps(pred_dict, default=str)

def deserialize_prediction(pred_json: str) -> Dict:
    """Deserialize prediction from JSON"""
    return json.loads(pred_json)

class PerformanceMonitor:
    """Monitor performance metrics"""
    
    def __init__(self):
        self.timings = {}
    
    def record_time(self, operation: str, duration_ms: float):
        """Record operation timing"""
        if operation not in self.timings:
            self.timings[operation] = []
        self.timings[operation].append(duration_ms)
    
    def get_avg_time(self, operation: str) -> float:
        """Get average time for operation"""
        if operation not in self.timings or not self.timings[operation]:
            return 0.0
        return sum(self.timings[operation]) / len(self.timings[operation])
    
    def get_summary(self) -> Dict:
        """Get performance summary"""
        return {
            op: self.get_avg_time(op) for op in self.timings
        }

if __name__ == "__main__":
    setup_logging('INFO')
    logger.info("Utils module initialized")
