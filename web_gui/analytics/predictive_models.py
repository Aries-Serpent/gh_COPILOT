"""Predictive model stubs for web GUI analytics."""

from __future__ import annotations

from typing import Sequence

from web_gui.monitoring.performance_metrics import collect_performance_metrics

__all__ = ["predict_next", "PerformancePredictor"]


def predict_next(values: Sequence[float] | None = None) -> float:
    """Predict next value from ``values`` or current CPU usage."""
    if values:
        if len(values) < 2:
            return float(values[-1])
        return float(values[-1] + (values[-1] - values[-2]))
    metrics = collect_performance_metrics()
    return metrics.get("cpu_percent", 0.0)


class PerformancePredictor:
    """Stub predictive model."""

    def predict(self, history: Sequence[float] | None = None) -> float:
        """Delegate to :func:`predict_next` for prediction."""
        return predict_next(history)
