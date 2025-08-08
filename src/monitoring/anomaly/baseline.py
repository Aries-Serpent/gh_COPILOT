"""Simple statistical anomaly detection models."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, Tuple
import csv

# Type alias for mean and standard deviation per metric
Model = Tuple[float, float]


def _load_values(file: Path) -> Iterable[float]:
    """Load numeric values from a CSV file.

    The file is expected to contain a header with a ``value`` column or a
    single unnamed column of numeric values.
    """
    values: list[float] = []
    with file.open() as fh:
        reader = csv.DictReader(fh)
        if "value" in reader.fieldnames if reader.fieldnames else []:
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
    """Train baseline models using historical metrics.

    The function reads all ``*.csv`` files under ``data_dir`` and computes the
    mean and standard deviation for each metric.  The resulting mapping uses
    the file stem (e.g. ``cpu_usage`` for ``cpu_usage.csv``) as the metric
    name.
    """
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
    """Detect anomalies given current metric values.

    Parameters
    ----------
    models:
        Mapping of metric name to ``(mean, std)`` tuple.
    current_metrics:
        Latest metric readings to evaluate.
    z_threshold:
        Z-score above which a metric is considered anomalous.  Default is ``3``.

    Returns
    -------
    Dict[str, bool]
        Mapping of metric name to ``True`` if the metric is anomalous.
    """
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
