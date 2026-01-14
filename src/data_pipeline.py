"""Data Pipeline for streaming transaction processing"""
import json
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import pandas as pd
import numpy as np
from kafka import KafkaConsumer
from kafka.errors import KafkaError
import psycopg2
from redis import Redis
from pydantic import BaseModel, validator

logger = logging.getLogger(__name__)

class TransactionRecord(BaseModel):
    """Pydantic model for transaction validation"""
    transaction_id: str
    customer_id: str
    amount: float
    merchant_id: str
    timestamp: str
    location: str
    device_id: str
    transaction_type: str
    card_present: bool
    
    @validator('amount')
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Amount must be positive')
        return v

class DataPipeline:
    """Main data pipeline orchestrator"""
    
    def __init__(self, kafka_brokers: List[str], db_config: Dict, redis_host: str = 'localhost'):
        self.kafka_brokers = kafka_brokers
        self.db_config = db_config
        self.redis_client = Redis(host=redis_host, port=6379, db=0)
        self.db_connection = None
        self.consumer = None
        
    def connect_database(self):
        """Establish PostgreSQL connection"""
        try:
            self.db_connection = psycopg2.connect(
                dbname=self.db_config['dbname'],
                user=self.db_config['user'],
                password=self.db_config['password'],
                host=self.db_config['host'],
                port=self.db_config['port']
            )
            logger.info("Database connection established")
        except psycopg2.Error as e:
            logger.error(f"Database connection failed: {e}")
            raise
    
    def validate_transaction(self, record: Dict) -> Tuple[bool, Optional[TransactionRecord], Optional[str]]:
        """Validate incoming transaction record"""
        try:
            transaction = TransactionRecord(**record)
            return True, transaction, None
        except Exception as e:
            logger.warning(f"Validation failed: {e}")
            return False, None, str(e)
    
    def preprocess_transaction(self, transaction: TransactionRecord) -> Dict:
        """Preprocess transaction for feature engineering"""
        processed = {
            'transaction_id': transaction.transaction_id,
            'customer_id': transaction.customer_id,
            'amount': float(transaction.amount),
            'merchant_id': transaction.merchant_id,
            'timestamp': transaction.timestamp,
            'location': transaction.location,
            'device_id': transaction.device_id,
            'transaction_type': transaction.transaction_type,
            'card_present': int(transaction.card_present),
            'processed_at': datetime.now().isoformat()
        }
        return processed
    
    def store_transaction(self, transaction: Dict) -> None:
        """Store transaction in PostgreSQL"""
        try:
            cursor = self.db_connection.cursor()
            query = """
                INSERT INTO transactions (transaction_id, customer_id, amount, merchant_id, timestamp, location, device_id, transaction_type, card_present)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (transaction_id) DO NOTHING
            """
            cursor.execute(query, (
                transaction['transaction_id'],
                transaction['customer_id'],
                transaction['amount'],
                transaction['merchant_id'],
                transaction['timestamp'],
                transaction['location'],
                transaction['device_id'],
                transaction['transaction_type'],
                transaction['card_present']
            ))
            self.db_connection.commit()
            cursor.close()
        except psycopg2.Error as e:
            logger.error(f"Database write failed: {e}")
            self.db_connection.rollback()

if __name__ == "__main__":
    # Example usage
    kafka_brokers = ['localhost:9092']
    db_config = {'dbname': 'fraud_detection', 'user': 'postgres', 'password': 'postgres', 'host': 'localhost', 'port': 5432}
    pipeline = DataPipeline(kafka_brokers, db_config)
