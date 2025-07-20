"""Additional demonstration algorithms for quantum library expansion."""

from __future__ import annotations

from typing import Iterable, List

import numpy as np
from qiskit.circuit import QuantumCircuit
from qiskit.circuit.library import QFT
from qiskit.quantum_info import DensityMatrix, Statevector
from qiskit_aer import AerSimulator

from scripts.utilities.quantum_algorithm_library_expansion import EnterpriseUtility

__all__ = [
    "EnterpriseUtility",
    "demo_grover_search",
    "demo_quantum_teleportation",
    "demo_quantum_fourier_transform",
]


def demo_grover_search() -> int:
    """Demo Grover search on a two-qubit space."""
    data = [0, 1, 2, 3]
    target = 3
    num_qubits = 2
    qc = QuantumCircuit(num_qubits, num_qubits)
    qc.h(range(num_qubits))

    def oracle(circ: QuantumCircuit) -> None:
        circ.cz(0, 1)

    def diffusion(circ: QuantumCircuit) -> None:
        circ.h(range(num_qubits))
        circ.x(range(num_qubits))
        circ.h(1)
        circ.cx(0, 1)
        circ.h(1)
        circ.x(range(num_qubits))
        circ.h(range(num_qubits))

    oracle(qc)
    diffusion(qc)
    qc.measure(range(num_qubits), range(num_qubits))
    backend = AerSimulator()
    counts = backend.run(qc, shots=200).result().get_counts()
    measured = max(counts, key=counts.get)
    return int(measured, 2)


def demo_quantum_teleportation(state: Iterable[complex] | None = None) -> List[List[complex]]:
    """Teleport ``state`` (default Bell) and return the resulting density matrix."""
    if state is None:
        state = [1 / np.sqrt(2), 1 / np.sqrt(2)]
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


def demo_quantum_fourier_transform() -> List[complex]:
    """Run a simple two-qubit QFT demonstration."""
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.h(1)
    qc.append(QFT(2, do_swaps=False), [0, 1])
    state = Statevector.from_instruction(qc)
    return state.data.tolist()

