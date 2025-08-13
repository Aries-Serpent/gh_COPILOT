"""Anomaly detection package.

This package provides utilities for training simple statistical models as
well as a small pipeline for training and evaluating anomaly detectors that
operate on historical metrics stored in a SQLite database.
"""

from .baseline import Model, detect_anomalies, train_baseline_models
from .model import StatisticalAnomalyDetector
from .pipeline import AnomalyPipeline

__all__ = [
    "train_baseline_models",
    "detect_anomalies",
    "AnomalyPipeline",
    "StatisticalAnomalyDetector",
    "Model",
]
