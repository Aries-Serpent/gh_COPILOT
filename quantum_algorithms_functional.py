"""Basic quantum algorithms implemented with Qiskit simulators.

This module exposes a small collection of reference implementations for common
quantum algorithms.  The implementations rely solely on the Qiskit simulator
backends so they can be executed in a unit-test environment without requiring
real quantum hardware.  These functions are intentionally lightweight and are
meant for demonstration and testing purposes only.
"""

from __future__ import annotations

import time
from typing import Iterable, List

import numpy as np
from qiskit.circuit import QuantumCircuit
from qiskit.circuit.library import QFT
from qiskit.quantum_info import DensityMatrix, Statevector
from qiskit_aer import AerSimulator
from sklearn.cluster import KMeans
from sklearn.datasets import make_blobs

try:
    from qiskit.algorithms import Shor
except Exception:  # pragma: no cover - fallback when algorithms module missing
    from copilot_qiskit_stubs.algorithms import Shor  # type: ignore


__all__ = [
    "run_grover_search",
    "run_kmeans_clustering",
    "run_shor_factorization",
    "run_quantum_fourier_transform",
    "run_variational_circuit",
    "run_quantum_teleportation",
]


def run_grover_search(data: List[int], target: int) -> dict:
    """Locate ``target`` in ``data`` using a Grover search circuit."""
    try:
        index = data.index(target)
    except ValueError:
        return {"index": -1, "iterations": 0}

    num_qubits = int(np.ceil(np.log2(len(data))))
    qc = QuantumCircuit(num_qubits, num_qubits)
    qc.h(range(num_qubits))

    def oracle(circ: QuantumCircuit) -> None:
        for q in range(num_qubits):
            if (index >> q) & 1 == 0:
                circ.x(q)
        if num_qubits == 1:
            circ.z(0)
        else:
            circ.h(num_qubits - 1)
            circ.mcx(list(range(num_qubits - 1)), num_qubits - 1)
            circ.h(num_qubits - 1)
        for q in range(num_qubits):
            if (index >> q) & 1 == 0:
                circ.x(q)

    def diffusion(circ: QuantumCircuit) -> None:
        circ.h(range(num_qubits))
        circ.x(range(num_qubits))
        if num_qubits == 1:
            circ.z(0)
        else:
            circ.h(num_qubits - 1)
            circ.mcx(list(range(num_qubits - 1)), num_qubits - 1)
            circ.h(num_qubits - 1)
        circ.x(range(num_qubits))
        circ.h(range(num_qubits))

    iterations = max(1, int(np.pi / 4 * np.sqrt(2**num_qubits)))
    for _ in range(iterations):
        oracle(qc)
        diffusion(qc)

    qc.measure(range(num_qubits), range(num_qubits))
    backend = AerSimulator()
    counts = backend.run(qc, shots=1024).result().get_counts()
    measured = max(counts, key=counts.get)
    return {"index": int(measured, 2), "iterations": iterations}


def run_kmeans_clustering(samples: int = 100, clusters: int = 2) -> dict:
    """Run KMeans clustering and return inertia and runtime."""
    features, _ = make_blobs(n_samples=samples, centers=clusters, random_state=42)
    start = time.perf_counter()
    model = KMeans(n_clusters=clusters, n_init="auto", random_state=42)
    model.fit(features)
    runtime = time.perf_counter() - start
    return {"inertia": float(model.inertia_), "time": runtime}


def run_shor_factorization(n: int) -> List[int]:
    """Factor ``n`` using Shor's algorithm (simulated)."""
    backend = AerSimulator()
    result = Shor(quantum_instance=backend).factor(n)
    return result.factors[0]


def run_quantum_fourier_transform(data: Iterable[float]) -> List[complex]:
    """Apply the QFT to ``data`` and return the resulting statevector."""
    data_list = list(data)
    num_qubits = int(np.log2(len(data_list)))
    qc = QuantumCircuit(num_qubits)
    qc.initialize(data_list, range(num_qubits), normalize=True)
    qc.append(QFT(num_qubits, do_swaps=False), range(num_qubits))
    state = Statevector.from_instruction(qc)
    return state.data.tolist()


def run_variational_circuit(steps: int = 20, lr: float = 0.1) -> dict:
    """Optimize a single-qubit rotation using a simple gradient descent."""
    theta = 0.0
    backend = AerSimulator()

    for _ in range(steps):
        qc = QuantumCircuit(1, 1)
        qc.ry(theta, 0)
        qc.measure(0, 0)
        counts = backend.run(qc, shots=1000).result().get_counts()
        prob0 = counts.get("0", 0) / 1000
        expectation = prob0 - (1 - prob0)
        grad = -np.sin(theta)
        theta -= lr * grad

    return {"theta": float(theta), "expectation": float(expectation)}


def run_quantum_teleportation(state: Iterable[complex]) -> List[List[complex]]:
    """Teleport a single-qubit ``state`` and return the final density matrix."""
    alpha, beta = list(state)
    qc = QuantumCircuit(3)
    qc.initialize([alpha, beta], 0)
    qc.h(1)
    qc.cx(1, 2)
    qc.cx(0, 1)
    qc.h(0)
    qc.cx(1, 2)
    qc.cz(0, 2)
    dm = DensityMatrix.from_instruction(qc)
    teleported = dm.reduce([2])
    return teleported.data.tolist()
