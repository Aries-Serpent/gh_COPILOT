"""Baseline anomaly detector using z-score from monitoring.db."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List
import sqlite3


@dataclass
class BaselineAnomalyDetector:
    """Detect anomalies via a simple z-score threshold."""

    threshold: float = 3.0
    db_path: Path = Path("databases/monitoring.db")
    metric: str = "system_health_score"

    def _fetch_values(self) -> List[float]:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute(f"SELECT {self.metric} FROM performance_metrics")
            return [row[0] for row in cur.fetchall() if row[0] is not None]

    def zscores(self) -> List[float]:
        values = self._fetch_values()
        if not values:
            return []
        mean = sum(values) / len(values)
        variance = sum((v - mean) ** 2 for v in values) / len(values)
        std = variance ** 0.5
        if std == 0:
            return [0.0 for _ in values]
        return [(v - mean) / std for v in values]

    def detect(self) -> List[bool]:
        return [abs(z) > self.threshold for z in self.zscores()]
