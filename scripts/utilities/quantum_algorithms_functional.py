#!/usr/bin/env python3
"""Utility wrappers for quantum functional algorithms."""
from __future__ import annotations

from ghc_quantum.algorithms.functional import QuantumFunctional

__all__ = [
    "run_grover_search",
    "run_kmeans_clustering",
    "run_simple_qnn",
    "run_shor_factorization",
    "run_quantum_fourier_transform",
    "run_variational_circuit",
    "run_quantum_teleportation",
]


def run_grover_search(data, target):
    """Run Grover search and return metrics."""
    return QuantumFunctional().run_grover_search(data, target)


def run_kmeans_clustering(samples=100, clusters=2, n_init=10):
    """Run KMeans clustering and return metrics."""
    return QuantumFunctional().run_kmeans_clustering(samples, clusters, n_init)


def run_simple_qnn():
    """Run simple QNN classifier and return metrics."""
    return QuantumFunctional().run_simple_qnn()


def run_shor_factorization(n: int):
    """Factor ``n`` using Shor's algorithm."""
    return QuantumFunctional().run_shor_factorization(n)


def run_quantum_fourier_transform(data):
    """Apply QFT to ``data`` and return the resulting statevector."""
    return QuantumFunctional().run_quantum_fourier_transform(data)


def run_variational_circuit(steps: int = 20, lr: float = 0.1):
    """Optimize a simple variational circuit."""
    return QuantumFunctional().run_variational_circuit(steps, lr)


def run_quantum_teleportation(state):
    """Teleport ``state`` and return final density matrix."""
    return QuantumFunctional().run_quantum_teleportation(state)


def main() -> bool:
    util = QuantumFunctional()
    return util.execute_utility()


if __name__ == "__main__":  # pragma: no cover - manual execution
    import sys
    sys.exit(0 if main() else 1)
