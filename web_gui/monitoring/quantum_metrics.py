"""Simulated quantum metrics for monitoring."""

from __future__ import annotations

from typing import Iterable

__all__ = ["quantum_metric"]


def quantum_metric(values: Iterable[float]) -> float:
    """Return a quantum-inspired score for the given values.

    Falls back to a simple average if quantum libraries are unavailable.
    """
    try:
        from quantum_algorithm_library_expansion import quantum_score_stub

        return float(quantum_score_stub(list(values)))
    except Exception:
        data = list(values)
        return float(sum(data) / len(data)) if data else 0.0
