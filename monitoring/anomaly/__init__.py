"""Anomaly detection utilities."""

from typing import Dict, Tuple

from .model import StatisticalAnomalyDetector

# Type alias for mean and standard deviation per metric
Model = Tuple[float, float]


def detect_anomalies(
    models: Dict[str, Model],
    current_metrics: Dict[str, float],
    *,
    z_threshold: float = 3.0,
) -> Dict[str, bool]:
    """Detect anomalies given current metric values."""

    anomalies: Dict[str, bool] = {}
    for metric, value in current_metrics.items():
        model = models.get(metric)
        if model is None:
            continue
        mean, std = model
        if std == 0:
            anomalies[metric] = value != mean
            continue
        z_score = abs(value - mean) / std
        anomalies[metric] = z_score > z_threshold
    return anomalies


__all__ = ["StatisticalAnomalyDetector", "Model", "detect_anomalies"]
