"""Performance analysis helpers."""

from __future__ import annotations

__all__ = ["calculate_throughput"]


def calculate_throughput(requests: int, seconds: float) -> float:
    """Return requests processed per second."""
    if seconds <= 0:
        return 0.0
    return requests / seconds
