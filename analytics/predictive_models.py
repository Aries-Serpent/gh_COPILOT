"""Simple predictive model helpers."""

from __future__ import annotations

from typing import Sequence

__all__ = ["predict_next"]


def predict_next(values: Sequence[float]) -> float:
    """Return the average as a naive prediction of the next value."""
    if not values:
        return 0.0
    return sum(values) / len(values)
