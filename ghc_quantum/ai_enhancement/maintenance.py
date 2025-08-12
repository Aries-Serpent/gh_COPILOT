"""Predictive maintenance helpers."""

from typing import Iterable


def predict_failure(metrics: Iterable[float]) -> float:
    """Return the average of *metrics* as a simple risk indicator.

    Raises
    ------
    ValueError
        If ``metrics`` is empty.
    """

    values = list(metrics)
    if not values:
        raise ValueError("metrics must not be empty")
    return sum(values) / len(values)


__all__ = ["predict_failure"]

