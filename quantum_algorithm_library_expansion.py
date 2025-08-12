"""Lightweight quantum algorithm demonstrations used in tests.

The real Qiskit dependency is intentionally avoided to keep the test
environment lightweight.  Algorithms are implemented using ``numpy``
only and are simplified versions of their quantum counterparts.
"""

from __future__ import annotations

import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Iterable, List

try:
    from qiskit import QuantumCircuit

    QISKIT_AVAILABLE = True
except Exception:  # pragma: no cover - qiskit optional
    QISKIT_AVAILABLE = False

import numpy as np
from sklearn.cluster import KMeans
from tqdm import tqdm

from ghc_quantum.advanced_quantum_algorithms import (
    grover_search_qiskit,
    phase_estimation_qiskit,
)
from ghc_quantum.utils.backend_provider import get_backend

ANALYTICS_DB = Path("databases/analytics.db")


def configure_backend(
    backend_name: str = "ibmq_qasm_simulator",
    use_hardware: bool | None = None,
    token: str | None = None,
):
    """Return a configured backend for Qiskit operations.

    Parameters mirror :func:`quantum.utils.backend_provider.get_backend` and
    allow supplying an IBM Quantum API ``token``. The function returns ``None``
    when no backend is available.
    """
    if token:
        os.environ.setdefault("QISKIT_IBM_TOKEN", token)
    return get_backend(backend_name, use_hardware=use_hardware)


def log_quantum_event(name: str, details: str) -> None:
    """Log quantum algorithm usage if ``analytics.db`` exists."""
    if not ANALYTICS_DB.exists():
        # Manual creation required; skip logging if database is absent
        return

    try:
        with sqlite3.connect(ANALYTICS_DB) as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS quantum_events (timestamp TEXT, name TEXT, details TEXT)")
            conn.execute(
                "INSERT INTO quantum_events (timestamp, name, details) VALUES (?, ?, ?)",
                (datetime.utcnow().isoformat(), name, details),
            )
            conn.commit()
    except sqlite3.Error:
        # Logging should not raise during optional analytics collection
        pass


class EnterpriseUtility:
    """Minimal enterprise utility wrapper used for testing."""

    def __init__(self, workspace_path: str | None = None) -> None:  # pragma: no cover - thin wrapper
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
    "demo_quantum_neural_network",
    "quantum_cluster_score",
    "quantum_similarity_score",
    "quantum_pattern_match_stub",
    "quantum_text_score",
    "configure_backend",
    "grover_search_qiskit",
    "phase_estimation_qiskit",
]


def demo_grover_search() -> int:
    """Return the target index found by a 2-qubit Grover search."""
    log_quantum_event("grover", "start")
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
    log_quantum_event("grover", f"result={index}")
    return index


def demo_shor_factorization(n: int = 15) -> List[int]:
    """Return two non-trivial factors of ``n`` using a naive search."""
    log_quantum_event("shor", str(n))
    for i in range(2, int(np.sqrt(n)) + 1):
        if n % i == 0:
            return [i, n // i]
    result = [n, 1]
    log_quantum_event("shor", f"result={result}")
    return result


def demo_quantum_teleportation(
    state: Iterable[complex] | None = None,
) -> List[List[complex]]:
    """Teleport ``state`` (default Bell) and return the resulting density matrix."""
    log_quantum_event("teleport", "start")
    if state is None:
        state = [1 / np.sqrt(2), 1 / np.sqrt(2)]
    alpha, beta = list(state)
    rho = np.array(
        [
            [abs(alpha) ** 2, alpha * np.conjugate(beta)],
            [np.conjugate(alpha) * beta, abs(beta) ** 2],
        ]
    )
    result = rho.tolist()
    log_quantum_event("teleport", "complete")
    return result


def demo_quantum_fourier_transform() -> List[complex]:
    """Run a simple two-qubit quantum Fourier transform."""
    log_quantum_event("qft", "start")
    h = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
    qft2 = np.kron(h, h)
    vec = np.array([1, 0, 0, 0], dtype=complex)
    result = (qft2 @ vec).tolist()
    log_quantum_event("qft", "complete")
    return result


def demo_variational_quantum_eigensolver(steps: int = 20, lr: float = 0.1) -> dict:
    """Minimize the expectation value of Z for a single qubit."""
    log_quantum_event("vqe", f"steps={steps}")
    theta = 0.0
    for _ in range(steps):
        grad = -np.sin(theta)
        theta -= lr * grad
    energy = np.cos(theta)
    result = {"theta": float(theta), "energy": float(energy)}
    log_quantum_event("vqe", "complete")
    return result


def demo_quantum_phase_estimation(theta: float = 0.25, precision: int = 3) -> float:
    """Estimate ``theta`` using a simple rounding-based simulation."""
    log_quantum_event("qpe", f"theta={theta}")
    factor = 2**precision
    estimate = round(theta * factor) / factor
    log_quantum_event("qpe", f"estimate={estimate}")
    return float(estimate)


def quantum_cluster_stub(data: Iterable[float]) -> List[int]:
    """Cluster one-dimensional ``data`` using :class:`~sklearn.cluster.KMeans`.

    The function groups the values into two clusters using a classical
    KMeans algorithm.  It mirrors the behaviour of a simple quantum
    clustering routine while remaining lightweight for testing
    environments that may not have access to quantum hardware.  The
    resulting cluster labels are returned in the order of the input
    sequence.
    """

    seq = np.fromiter(data, dtype=float).reshape(-1, 1)
    if seq.size == 0:
        return []
    log_quantum_event("cluster_stub", f"len={seq.size}")
    model = KMeans(n_clusters=min(2, len(seq)), n_init="auto", random_state=0)
    labels = model.fit_predict(seq)
    return labels.tolist()


def quantum_cluster_representatives(data: Iterable[str], n_clusters: int) -> List[str]:
    """Return representative strings for each cluster using KMeans."""
    log_quantum_event("cluster_reps", f"n={n_clusters}")
    items = list(data)
    if not items:
        return []
    n_clusters = min(n_clusters, len(items))
    # Encode each string by length and average character ordinal
    features = np.array(
        [[len(s), float(np.mean([ord(c) for c in s]))] for s in items],
        dtype=float,
    )
    model = KMeans(n_clusters=n_clusters, n_init="auto", random_state=0)
    labels = model.fit_predict(features)
    representatives: List[str] = []
    for i in range(n_clusters):
        idx = np.where(labels == i)[0]
        center = model.cluster_centers_[i]
        cluster_features = features[idx]
        distances = np.linalg.norm(cluster_features - center, axis=1)
        representatives.append(items[idx[np.argmin(distances)]])
    return representatives


def quantum_similarity_score(a: Iterable[float], b: Iterable[float]) -> float:
    """Return simple normalized dot product as quantum-inspired score."""
    arr_a = np.fromiter(a, dtype=float)
    arr_b = np.fromiter(b, dtype=float)
    min_len = min(arr_a.size, arr_b.size)
    if min_len == 0:
        return 0.0
    arr_a = arr_a[:min_len]
    arr_b = arr_b[:min_len]
    denom = np.linalg.norm(arr_a) * np.linalg.norm(arr_b)
    if denom == 0:
        return 0.0
    score = float(np.dot(arr_a, arr_b) / denom)
    log_quantum_event("similarity_score", str(score))
    return score


def quantum_score_stub(values: Iterable[float]) -> float:
    """Return a normalized Euclidean norm of ``values``.

    Values are interpreted as amplitudes of a simulated quantum state.
    The score is the L2 norm of the vector divided by its length,
    providing a scale-invariant measure of magnitude.
    """

    arr = np.fromiter(values, dtype=float)
    if arr.size == 0:
        return 0.0
    score = float(np.linalg.norm(arr) / arr.size)
    log_quantum_event("score_stub", str(score))
    return score


def quantum_cluster_score(matrix: np.ndarray) -> float:
    """Return a simple cluster-based score for ``matrix``."""
    log_quantum_event("cluster_score", f"shape={matrix.shape}")
    n_clusters = min(len(matrix), 2)
    model = KMeans(n_clusters=n_clusters, n_init="auto", random_state=0)
    labels = model.fit_predict(matrix)
    score = float(np.sum(labels) / (len(labels) or 1))
    log_quantum_event("cluster_score", str(score))
    return score


def demo_quantum_neural_network(data: Iterable[float]) -> List[float]:
    """Return output of a stub quantum neural network."""
    seq = list(data)
    log_quantum_event("qnn", f"len={len(seq)}")
    result = []
    for val in tqdm(seq, desc="qnn", unit="item"):
        result.append(val * 0.5)
    return result


def quantum_pattern_match_stub(pattern: Iterable[int], data: Iterable[int]) -> bool:
    """Return ``True`` if ``pattern`` is found in ``data`` using KMP.

    The Knuth–Morris–Pratt algorithm is employed to locate the pattern
    efficiently within the data sequence.  This provides a more
    algorithmically meaningful implementation than the previous
    placeholder.
    """

    pat = list(pattern)
    seq = list(data)
    if not pat:
        log_quantum_event("pattern_match", "trivial")
        return True

    # Pre-compute longest-prefix-suffix table
    lps = [0] * len(pat)
    j = 0
    for i in range(1, len(pat)):
        while j > 0 and pat[i] != pat[j]:
            j = lps[j - 1]
        if pat[i] == pat[j]:
            j += 1
            lps[i] = j

    # Scan the data using the prefix table
    j = 0
    for val in seq:
        while j > 0 and val != pat[j]:
            j = lps[j - 1]
        if val == pat[j]:
            j += 1
            if j == len(pat):
                log_quantum_event("pattern_match", "found")
                return True
    log_quantum_event("pattern_match", "not_found")
    return False


def quantum_text_score(
    text: str,
    use_hardware: bool | None = None,
    backend_name: str = "ibmq_qasm_simulator",
    token: str | None = None,
) -> float:
    """Return a quantum-inspired text score.

    When Qiskit is available, the function obtains a backend via
    :func:`configure_backend`, which prefers IBM Quantum hardware when
    ``use_hardware`` is True. If no backend is available or Qiskit is not
    installed, the function falls back to a simple classical heuristic. The
    execution path is logged to ``analytics.db`` via :func:`log_quantum_event`.
    """
    if QISKIT_AVAILABLE:
        backend = configure_backend(
            backend_name=backend_name, use_hardware=use_hardware, token=token
        )
        if backend is not None:
            circ = QuantumCircuit(1, 1)
            theta = (sum(map(ord, text)) % 360) * np.pi / 180
            circ.ry(theta, 0)
            circ.measure(0, 0)
            result = backend.run(circ, shots=256).result()
            counts = result.get_counts()
            score = counts.get("1", 0) / 256
            log_quantum_event("text_score", "qiskit")
            return float(score)

    arr = np.fromiter((ord(c) for c in text), dtype=float)
    score = float(np.linalg.norm(arr) / ((arr.size or 1) * 255))
    log_quantum_event("text_score", "simulated")
    return score
