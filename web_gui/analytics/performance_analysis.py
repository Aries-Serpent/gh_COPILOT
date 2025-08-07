"""Performance analysis helpers for the web GUI."""

from __future__ import annotations

from web_gui.monitoring.performance_metrics import collect_performance_metrics

__all__ = ["summarize_performance", "PerformanceAnalyzer"]


def summarize_performance() -> float:
    """Return the average of collected performance metrics."""
    metrics = collect_performance_metrics()
    return sum(metrics.values()) / len(metrics) if metrics else 0.0


class PerformanceAnalyzer:
    """Stub analyzer that delegates to :func:`summarize_performance`."""

    def summarize(self) -> float:
        """Return summary statistics for current performance metrics."""
        return summarize_performance()
