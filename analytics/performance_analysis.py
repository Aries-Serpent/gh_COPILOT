"""Simple performance analysis helpers."""

from __future__ import annotations

from typing import Dict

__all__ = ["summarize_performance"]


def summarize_performance(metrics: Dict[str, float]) -> float:
    """Return the average value of the provided metrics."""
    if not metrics:
        return 0.0
    return sum(metrics.values()) / len(metrics)
