"""Anomaly detection utilities using statistical and machine learning models."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import sqlite3
from sklearn.ensemble import IsolationForest


@dataclass
class MetricModel:
    """Container for per-metric anomaly detection models."""

    mean: float
    std: float
    isolation_forest: IsolationForest


def _load_metrics(db_path: Path) -> Dict[str, List[float]]:
    """Load historical metric values from ``analytics.db``.

    The database is expected to contain a table named ``sync_metrics`` with
    columns ``metric`` (text) and ``value`` (numeric).
    """

    conn = sqlite3.connect(db_path)
    try:
        cur = conn.execute("SELECT metric, value FROM sync_metrics")
        metrics: Dict[str, List[float]] = {}
        for metric, value in cur:
            try:
                v = float(value)
            except (TypeError, ValueError):
                continue
            metrics.setdefault(metric, []).append(v)
    finally:
        conn.close()
    return metrics


def train_models(db_path: Path) -> Dict[str, MetricModel]:
    """Train baseline models using historical metrics from ``db_path``."""

    metrics = _load_metrics(db_path)
    models: Dict[str, MetricModel] = {}
    for metric, values in metrics.items():
        if not values:
            continue
        mean = sum(values) / len(values)
        variance = sum((v - mean) ** 2 for v in values) / len(values)
        std = variance ** 0.5
        forest = IsolationForest(random_state=0).fit([[v] for v in values])
        models[metric] = MetricModel(mean, std, forest)
    return models


def detect_anomalies(
    data: Dict[str, float],
    models: Dict[str, MetricModel],
    *,
    z_threshold: float = 3.0,
) -> Dict[str, bool]:
    """Return flags for metrics that appear anomalous.

    A metric is flagged if either the z-score exceeds ``z_threshold`` or the
    Isolation Forest model predicts it as an outlier.
    """

    anomalies: Dict[str, bool] = {}
    for metric, value in data.items():
        model = models.get(metric)
        if model is None:
            continue
        if model.std == 0:
            z_flag = value != model.mean
        else:
            z_flag = abs(value - model.mean) / model.std > z_threshold
        iso_flag = model.isolation_forest.predict([[value]])[0] == -1
        anomalies[metric] = z_flag or iso_flag
    return anomalies


__all__ = ["MetricModel", "train_models", "detect_anomalies"]

