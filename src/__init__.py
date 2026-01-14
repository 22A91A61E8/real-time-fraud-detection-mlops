"""Fraud Detection System Package"""

__version__ = "1.0.0"
__author__ = "Fraud Detection Team"

from src import (
    data_pipeline,
    feature_engineering,
    model_training,
    prediction,
    monitoring,
    api,
)

__all__ = [
    "data_pipeline",
    "feature_engineering",
    "model_training",
    "prediction",
    "monitoring",
    "api",
]
