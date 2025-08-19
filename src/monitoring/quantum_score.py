"""Deterministic quantum-inspired scoring utilities."""

from __future__ import annotations

from math import sqrt
from typing import Iterable

__all__ = ["quantum_score", "normalized_variance"]


def quantum_score(values: Iterable[float]) -> float:
    """Return a normalized Euclidean norm of ``values``.

    This function provides a deterministic placeholder for a future
    quantum-based scoring algorithm. It computes the L2 norm of the
    supplied vector and normalizes it by the vector length to keep the
    score scale-invariant.
    """

    data = [float(v) for v in values]
    if not data:
        return 0.0
    norm = sqrt(sum(v * v for v in data))
    return norm / len(data)


def normalized_variance(values: Iterable[float]) -> float:
    """Return variance normalized by the mean of ``values``.

    The function computes the population variance and scales it by the
    absolute mean to keep the result roughly order-invariant.  It returns
    ``0.0`` for empty or single-element inputs to avoid division errors.
    """

    data = [float(v) for v in values]
    if len(data) < 2:
        return 0.0
    mean = sum(data) / len(data)
    if mean == 0:
        return 0.0
    variance = sum((v - mean) ** 2 for v in data) / len(data)
    return variance / abs(mean)
