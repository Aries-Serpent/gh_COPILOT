#!/usr/bin/env python3
"""Utility wrappers for quantum functional algorithms."""
from __future__ import annotations

from quantum.algorithms.functional import QuantumFunctional

__all__ = [
    "run_grover_search",
    "run_kmeans_clustering",
    "run_simple_qnn",
]


def run_grover_search(data, target):
    """Run Grover search and return metrics."""
    return QuantumFunctional().run_grover_search(data, target)


def run_kmeans_clustering(samples=100, clusters=2):
    """Run KMeans clustering and return metrics."""
    return QuantumFunctional().run_kmeans_clustering(samples, clusters)


def run_simple_qnn():
    """Run simple QNN classifier and return metrics."""
    return QuantumFunctional().run_simple_qnn()


def main() -> bool:
    util = QuantumFunctional()
    return util.execute_utility()


if __name__ == "__main__":  # pragma: no cover - manual execution
    import sys
    sys.exit(0 if main() else 1)
