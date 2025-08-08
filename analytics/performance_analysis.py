"""Simple performance analysis helpers."""

from __future__ import annotations

from typing import Dict

__all__ = ["summarize_performance", "calculate_throughput"]


def summarize_performance(metrics: Dict[str, float]) -> float:
    """Return the average value of the provided metrics."""
    if not metrics:
        return 0.0
    return sum(metrics.values()) / len(metrics)


def calculate_throughput(total: float, duration: float) -> float:
    """Return items processed per unit time.

    A ``duration`` of ``0`` yields ``0.0`` to avoid a division-by-zero error.
    """

    if duration <= 0:
        return 0.0
    return total / duration
