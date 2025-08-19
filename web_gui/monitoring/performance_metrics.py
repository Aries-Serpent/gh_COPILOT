"""Collect performance metrics for the web GUI."""

from __future__ import annotations

import json
import logging
from typing import Dict, Protocol

try:  # pragma: no cover - handled via runtime check
    import psutil  # type: ignore
except ImportError:  # pragma: no cover - executed when psutil missing
    psutil = None  # type: ignore
    logging.getLogger(__name__).warning(
        "psutil not installed; performance metrics will be mocked"
    )

__all__ = [
    "PerformanceMetricsCollector",
    "DictExporter",
    "JsonExporter",
    "collect_performance_metrics",
]


class MetricCollector(Protocol):
    """Protocol for metric collectors."""

    def collect(self) -> Dict[str, float]:
        """Collect metrics and return a mapping."""


class MetricExporter(Protocol):
    """Protocol for metric exporters."""

    def export(self, metrics: Dict[str, float]):
        """Export metrics in a desired format."""


class PerformanceMetricsCollector:
    """Gather basic system performance metrics using :mod:`psutil`."""

    def collect(self) -> Dict[str, float]:
        if psutil is None:
            # psutil is unavailable; return mocked metrics
            return {"cpu_percent": 0.0, "memory_percent": 0.0}

        return {
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "memory_percent": psutil.virtual_memory().percent,
        }


class DictExporter:
    """Return metrics unchanged as a dictionary."""

    def export(self, metrics: Dict[str, float]) -> Dict[str, float]:
        return metrics


class JsonExporter:
    """Serialize metrics as a JSON string."""

    def export(self, metrics: Dict[str, float]) -> str:
        return json.dumps(metrics)


def collect_performance_metrics() -> Dict[str, float]:
    """Return basic system performance metrics as a dictionary."""
    collector = PerformanceMetricsCollector()
    exporter = DictExporter()
    return exporter.export(collector.collect())
