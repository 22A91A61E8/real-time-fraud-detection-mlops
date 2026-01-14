"""Configuration Management for Fraud Detection System"""
import os
from typing import Dict, Any
from pydantic import BaseSettings

class Settings(BaseSettings):
    """Application settings"""
    app_name: str = "Real-Time Fraud Detection"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Kafka Configuration
    kafka_brokers: str = os.getenv("KAFKA_BROKERS", "localhost:9092")
    kafka_topic: str = os.getenv("KAFKA_TOPIC", "transactions")
    kafka_group_id: str = os.getenv("KAFKA_GROUP_ID", "fraud-detection-group")
    
    # Database Configuration
    db_host: str = os.getenv("DB_HOST", "localhost")
    db_port: int = int(os.getenv("DB_PORT", "5432"))
    db_name: str = os.getenv("DB_NAME", "fraud_detection")
    db_user: str = os.getenv("DB_USER", "postgres")
    db_password: str = os.getenv("DB_PASSWORD", "postgres")
    
    # Redis Configuration
    redis_host: str = os.getenv("REDIS_HOST", "localhost")
    redis_port: int = int(os.getenv("REDIS_PORT", "6379"))
    redis_db: int = int(os.getenv("REDIS_DB", "0"))
    
    # Model Configuration
    model_type: str = os.getenv("MODEL_TYPE", "xgboost")
    model_path: str = os.getenv("MODEL_PATH", "models/fraud_detector.pkl")
    scaler_path: str = os.getenv("SCALER_PATH", "models/scaler.pkl")
    prediction_threshold: float = float(os.getenv("PREDICTION_THRESHOLD", "0.5"))
    
    # API Configuration
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))
    api_workers: int = int(os.getenv("API_WORKERS", "4"))
    
    # Monitoring Configuration
    metrics_port: int = int(os.getenv("METRICS_PORT", "8001"))
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()

def get_db_config() -> Dict[str, Any]:
    """Get database configuration"""
    return {
        'dbname': settings.db_name,
        'user': settings.db_user,
        'password': settings.db_password,
        'host': settings.db_host,
        'port': settings.db_port
    }

def get_kafka_config() -> Dict[str, Any]:
    """Get Kafka configuration"""
    return {
        'brokers': settings.kafka_brokers.split(','),
        'topic': settings.kafka_topic,
        'group_id': settings.kafka_group_id
    }

def get_redis_config() -> Dict[str, Any]:
    """Get Redis configuration"""
    return {
        'host': settings.redis_host,
        'port': settings.redis_port,
        'db': settings.redis_db
    }
