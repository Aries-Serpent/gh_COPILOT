"""Physics optimization algorithms implemented with Qiskit."""
from __future__ import annotations

import math
from typing import Any, List

import numpy as np


class PhysicsOptimizationEngine:
    """Collection of quantum-inspired algorithms using Qiskit."""

    def grover_search(self, search_space: List[Any], target: Any) -> int:
        """Return the index of ``target`` using Grover's algorithm.

        If Qiskit is unavailable, fall back to a classical search.
        """
        try:
            from qiskit import QuantumCircuit
            from qiskit_aer import AerSimulator
        except Exception:  # pragma: no cover - qiskit missing
            for idx, item in enumerate(search_space):
                if item == target:
                    return idx
            return -1

        if target not in search_space:
            return -1

        n = len(search_space)
        num_qubits = max(1, math.ceil(math.log2(n)))
        index = search_space.index(target)

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

        iterations = max(1, int(math.pi / 4 * math.sqrt(2 ** num_qubits)))
        for _ in range(iterations):
            oracle(qc)
            diffusion(qc)

        qc.measure(range(num_qubits), range(num_qubits))
        backend = AerSimulator()
        counts = backend.run(qc, shots=1024).result().get_counts()
        measured = max(counts, key=counts.get)
        result_index = int(measured, 2)
        within_bounds = result_index < len(search_space)
        if within_bounds and search_space[result_index] == target:
            return result_index
        return -1

    def shor_factorization(self, n: int) -> List[int]:
        """Factor integer ``n`` using Shor's algorithm with fallback."""
        try:
            from qiskit.algorithms import Shor
            from qiskit_aer import AerSimulator
        except Exception:  # pragma: no cover - qiskit missing
            if n < 2:
                return []
            for i in range(2, int(math.sqrt(n)) + 1):
                if n % i == 0:
                    return [i, n // i]
            return [n]

        backend = AerSimulator()
        result = Shor(quantum_instance=backend).factor(n)
        factors = result.factors
        if factors:
            return list(factors[0])
        return [n]

    def fourier_transform(self, data: List[complex]) -> List[complex]:
        """Return the discrete Fourier transform of ``data`` via QFT."""
        try:
            from qiskit import QuantumCircuit
            from qiskit.circuit.library import QFT
            from qiskit.quantum_info import Statevector
        except Exception:  # pragma: no cover - qiskit missing
            return np.fft.fft(np.array(data)).tolist()

        n = len(data)
        num_qubits = int(math.log2(n))
        if 2 ** num_qubits != n:
            raise ValueError("Data length must be a power of 2")

        qc = QuantumCircuit(num_qubits)
        qc.initialize(data, range(num_qubits))
        qc.append(QFT(num_qubits, do_swaps=False), range(num_qubits))
        state = Statevector.from_instruction(qc)
        return state.data.tolist()


__all__ = ["PhysicsOptimizationEngine"]