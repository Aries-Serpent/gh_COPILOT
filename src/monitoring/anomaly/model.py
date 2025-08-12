"""Baseline statistical anomaly detection model."""
from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from pathlib import Path
from typing import Iterable, List
import json


@dataclass
class StatisticalAnomalyDetector:
    """Simple anomaly detector based on mean and standard deviation.

    The model computes mean and standard deviation from historical metrics
    and flags values as anomalies when they fall outside a configurable
    number of standard deviations from the mean.
    """

    threshold: float = 3.0
    mean: float = 0.0
    std: float = 0.0

    def train(self, metrics_path: Path | str = Path("analytics/historical_metrics.json")) -> None:
        """Train model using metrics stored in ``analytics`` directory."""
        path = Path(metrics_path)
        data = json.loads(path.read_text())
        values = data.get("metrics", [])
        if not values:
            raise ValueError("No metrics available for training")
        self.mean = sum(values) / len(values)
        variance = sum((v - self.mean) ** 2 for v in values) / len(values)
        self.std = sqrt(variance)

    def detect(self, values: Iterable[float]) -> List[bool]:
        """Return list indicating whether each ``value`` is an anomaly."""
        if self.std == 0:
            return [False for _ in values]
        return [abs(v - self.mean) > self.threshold * self.std for v in values]
