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

    def __init__(
        self, workspace_path: str | None = None
    ) -> None:  # pragma: no cover - thin wrapper
        """Initialize utility; workspace path is optional."""
        self.workspace_path = workspace_path

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
    "quantum_cluster_stub",
    "quantum_score_stub",
    "quantum_pattern_match_stub",
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


def demo_quantum_teleportation(
    state: Iterable[complex] | None = None,
) -> List[List[complex]]:
    """Teleport ``state`` (default Bell) and return the resulting density matrix."""
    if state is None:
        state = [1 / np.sqrt(2), 1 / np.sqrt(2)]
    alpha, beta = list(state)
    rho = np.array(
        [
            [abs(alpha) ** 2, alpha * np.conjugate(beta)],
            [np.conjugate(alpha) * beta, abs(beta) ** 2],
        ]
    )
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


def demo_quantum_phase_estimation(theta: float = 0.25, precision: int = 3) -> float:
    """Estimate ``theta`` using a simple rounding-based simulation."""
    factor = 2**precision
    estimate = round(theta * factor) / factor
    return float(estimate)


def quantum_cluster_stub(data: Iterable[float]) -> List[int]:
    """Return cluster labels using a placeholder algorithm."""
    labels = []
    for i, _ in enumerate(data):
        labels.append(i % 2)
    return labels


def quantum_score_stub(values: Iterable[float]) -> float:
    """Return a fake quantum-inspired score."""
    arr = np.fromiter(values, dtype=float)
    return float(np.sum(arr) / (len(arr) + 1))


def quantum_pattern_match_stub(pattern: Iterable[int], data: Iterable[int]) -> bool:
    """Return True if pattern is found in data."""
    seq = list(data)
    pat = list(pattern)
    for i in range(len(seq) - len(pat) + 1):
        if seq[i : i + len(pat)] == pat:
            return True
    return False
