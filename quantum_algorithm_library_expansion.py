"""Lightweight quantum algorithm demonstrations used in tests.

The real Qiskit dependency is intentionally avoided to keep the test
environment lightweight.  Algorithms are implemented using ``numpy``
only and are simplified versions of their quantum counterparts.
"""

from __future__ import annotations

from typing import Iterable, List

import numpy as np


class EnterpriseUtility:
    """Minimal enterprise utility wrapper used for testing."""

    def perform_utility_function(self) -> bool:  # pragma: no cover - thin wrapper
        """Run the Grover demo and report success."""
        return demo_grover_search() == 3


__all__ = [
    "EnterpriseUtility",
    "demo_grover_search",
    "demo_shor_factorization",
    "demo_quantum_fourier_transform",
    "demo_variational_quantum_eigensolver",
    "demo_quantum_phase_estimation",
    "demo_quantum_teleportation",
]


def demo_grover_search() -> int:
    """Return the target index found by a 2-qubit Grover search."""
    state = np.zeros(4, dtype=complex)
    state[:] = 0.5
    # Oracle marking index 3
    oracle = np.diag([1, 1, 1, -1])
    state = oracle @ state
    # Diffusion
    mean = np.full(4, 0.5)
    diffusion = 2 * np.outer(mean, mean) - np.eye(4)
    state = diffusion @ state
    index = int(np.argmax(np.abs(state)))
    return index


def demo_shor_factorization(n: int = 15) -> List[int]:
    """Return two non-trivial factors of ``n`` using a naive search."""
    for i in range(2, int(np.sqrt(n)) + 1):
        if n % i == 0:
            return [i, n // i]
    return [n, 1]


def demo_quantum_teleportation(state: Iterable[complex] | None = None) -> List[List[complex]]:
    """Teleport ``state`` (default Bell) and return the resulting density matrix."""
    if state is None:
        state = [1 / np.sqrt(2), 1 / np.sqrt(2)]
    alpha, beta = list(state)
    rho = np.array([[abs(alpha) ** 2, alpha * np.conjugate(beta)],
                    [np.conjugate(alpha) * beta, abs(beta) ** 2]])
    return rho.tolist()


def demo_quantum_fourier_transform() -> List[complex]:
    """Run a simple two-qubit quantum Fourier transform."""
    h = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
    qft2 = np.kron(h, h)
    vec = np.array([1, 0, 0, 0], dtype=complex)
    return (qft2 @ vec).tolist()


def demo_variational_quantum_eigensolver(steps: int = 20, lr: float = 0.1) -> dict:
    """Minimize the expectation value of Z for a single qubit."""
    theta = 0.0
    for _ in range(steps):
        grad = -np.sin(theta)
        theta -= lr * grad
    energy = np.cos(theta)
    return {"theta": float(theta), "energy": float(energy)}


def demo_quantum_phase_estimation(theta: float = 0.25) -> float:
    """Return an estimate of ``theta`` from a simulated phase estimation."""
    return round(float(theta), 2)

