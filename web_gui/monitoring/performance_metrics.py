"""Collect performance metrics for the web GUI."""

from __future__ import annotations

import json
import psutil
from typing import Dict, Protocol

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
