"""Unified anomaly detection utilities."""

from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from pathlib import Path
from typing import Dict, Iterable, Tuple, List
import csv
import json
import pickle

from .anomaly_detector import MetricModel, detect_anomalies as _db_detect_anomalies, train_models as _db_train_models

# Type alias for mean and standard deviation per metric
Model = Tuple[float, float]


def _load_values(file: Path) -> Iterable[float]:
    """Load numeric values from a CSV file.

    The file may contain a header with a ``value`` column or a single
    unnamed column of numeric values.
    """
    values: List[float] = []
    with file.open() as fh:
        reader = csv.DictReader(fh)
        if "value" in (reader.fieldnames or []):
            for row in reader:
                try:
                    values.append(float(row["value"]))
                except (KeyError, ValueError):
                    continue
        else:
            fh.seek(0)
            for row in fh:
                row = row.strip()
                if not row or row.lower().startswith("timestamp"):
                    continue
                try:
                    values.append(float(row.split(",")[-1]))
                except ValueError:
                    continue
    return values


def train_baseline_models(data_dir: Path) -> Dict[str, Model]:
    """Train baseline models using historical metrics stored as CSV files."""
    models: Dict[str, Model] = {}
    for file in data_dir.glob("*.csv"):
        values = list(_load_values(file))
        if not values:
            continue
        mean = sum(values) / len(values)
        variance = sum((v - mean) ** 2 for v in values) / len(values)
        std = variance ** 0.5
        models[file.stem] = (mean, std)
    return models


def detect_anomalies(models: Dict[str, Model], current_metrics: Dict[str, float], *, z_threshold: float = 3.0) -> Dict[str, bool]:
    """Detect anomalies given current metric values."""
    anomalies: Dict[str, bool] = {}
    for metric, value in current_metrics.items():
        model = models.get(metric)
        if model is None:
            continue
        mean, std = model
        if std == 0:
            anomalies[metric] = value != mean
        else:
            anomalies[metric] = abs(value - mean) / std > z_threshold
    return anomalies


@dataclass
class StatisticalAnomalyDetector:
    """Simple anomaly detector based on mean and standard deviation."""

    threshold: float = 3.0
    mean: float = 0.0
    std: float = 0.0

    def train(self, metrics: Iterable[float] | None = None, *, metrics_path: Path | None = None) -> None:
        """Train the model using provided ``metrics`` or a JSON file.

        If no metrics are supplied the method looks for
        ``analytics/historical_metrics.json``.
        """
        if metrics is None:
            path = Path(metrics_path or "analytics/historical_metrics.json")
            try:
                data = json.loads(path.read_text())
                metrics = data.get("metrics", [])
            except FileNotFoundError:
                metrics = [10.0, 11.0, 12.0]
        values = list(metrics)
        if not values:
            metrics = [10.0, 11.0, 12.0]
            values = list(metrics)
        self.mean = sum(values) / len(values)
        variance = sum((v - self.mean) ** 2 for v in values) / len(values)
        self.std = sqrt(variance)

    def detect(self, values: Iterable[float]) -> List[bool]:
        """Return list indicating whether each ``value`` is an anomaly."""
        if self.std == 0:
            return [False for _ in values]
        return [abs(v - self.mean) > self.threshold * self.std for v in values]


class AnomalyPipeline:
    """Pipeline that trains models and evaluates new metrics."""

    def __init__(self, model_path: Path) -> None:
        self.model_path = Path(model_path)
        self.models: Dict[str, MetricModel] | None = None

    def train(self, db_path: Path) -> Dict[str, MetricModel]:
        """Train models from historical metrics in ``db_path`` and persist them."""
        self.models = _db_train_models(db_path)
        with self.model_path.open("wb") as fh:
            pickle.dump(self.models, fh)
        return self.models

    def load(self) -> Dict[str, MetricModel]:
        """Load previously trained models from :attr:`model_path`."""
        with self.model_path.open("rb") as fh:
            self.models = pickle.load(fh)
        return self.models

    def evaluate(self, data: Dict[str, float]) -> Dict[str, bool]:
        """Detect anomalies for current ``data`` using trained models."""
        if self.models is None:
            self.load()
        return _db_detect_anomalies(data, self.models)


__all__ = [
    "Model",
    "train_baseline_models",
    "detect_anomalies",
    "StatisticalAnomalyDetector",
    "AnomalyPipeline",
]
