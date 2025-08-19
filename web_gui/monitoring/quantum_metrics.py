"""Simulated quantum metrics for monitoring."""

from __future__ import annotations

from typing import Dict, Iterable

from monitoring.quantum_score import quantum_score

__all__ = [
    "quantum_metric",
    "QuantumMetricsCollector",
    "DictExporter",
    "collect_quantum_metrics",
]


def quantum_metric(values: Iterable[float]) -> float:
    """Return a quantum-inspired score for the given values."""

    return float(quantum_score(list(values)))


class QuantumMetricsCollector:
    """Collect quantum-related metrics for a series of values."""

    def collect(self, values: Iterable[float]) -> Dict[str, float]:
        return {"quantum_score": quantum_metric(values)}


class DictExporter:
    """Return quantum metrics as a dictionary."""

    def export(self, metrics: Dict[str, float]) -> Dict[str, float]:
        return metrics


def collect_quantum_metrics(values: Iterable[float]) -> Dict[str, float]:
    """Collect and export quantum metrics for *values*."""
    collector = QuantumMetricsCollector()
    exporter = DictExporter()
    return exporter.export(collector.collect(values))
