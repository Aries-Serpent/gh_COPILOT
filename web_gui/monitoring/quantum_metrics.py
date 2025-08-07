"""Simulated quantum metrics for monitoring."""

from __future__ import annotations

from typing import Iterable

from quantum_algorithm_library_expansion import quantum_score_stub

__all__ = ["quantum_metric"]


def quantum_metric(values: Iterable[float]) -> float:
    """Return a quantum-inspired score for the given values."""
    return float(quantum_score_stub(list(values)))
