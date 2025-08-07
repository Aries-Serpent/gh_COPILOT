"""Naive predictive models."""

from __future__ import annotations

from typing import Sequence

__all__ = ["predict_next"]


def predict_next(values: Sequence[float]) -> float:
    """Predict the next value using the last observed delta."""
    if not values:
        return 0.0
    if len(values) < 2:
        return float(values[-1])
    return float(values[-1] + (values[-1] - values[-2]))
