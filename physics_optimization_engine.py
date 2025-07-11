"""Physics optimization algorithms using Qiskit.

This module provides quantum implementations for common operations
such as Grover search, Shor factorization, and the Quantum Fourier
Transform (QFT).  Classical fallbacks are included for environments
where Qiskit is not available.
"""

from __future__ import annotations

from math import ceil, log2
from typing import Any, Iterable, List

import numpy as np

try:  # Optional import as qiskit may not be installed
    from qiskit import Aer, QuantumCircuit
    from qiskit.algorithms import Grover, Shor, AmplificationProblem
    from qiskit.circuit.library import PhaseOracle, QFT
    from qiskit.quantum_info import Statevector

    _QISKIT_AVAILABLE = True
except Exception:  # pragma: no cover - handled gracefully if missing
    _QISKIT_AVAILABLE = False

class PhysicsOptimizationEngine:
    """Collection of quantum optimization methods."""

    def __init__(self) -> None:
        if _QISKIT_AVAILABLE:
            self.backend = Aer.get_backend("aer_simulator")
        else:  # pragma: no cover - executed if Qiskit missing
            self.backend = None

    def _ensure_power_of_two(self, length: int) -> int:
        n = ceil(log2(length))
        if 2 ** n != length:
            raise ValueError("Input length must be a power of 2")
        return n

    def grover_search(self, search_space: List[Any], target: Any) -> int:
        """Return the index of ``target`` using Grover's algorithm.

        Falls back to classical search when Qiskit is unavailable.
        """
        try:
            idx = search_space.index(target)
        except ValueError:
            return -1

        if not _QISKIT_AVAILABLE:
            return idx

        n = self._ensure_power_of_two(len(search_space))
        bitstring = bin(idx)[2:].zfill(n)[::-1]
        expr_parts = [f"{'~' if bit == '0' else ''}x{i}" for i, bit in enumerate(bitstring)]
        oracle = PhaseOracle(" & ".join(expr_parts))
        problem = AmplificationProblem(oracle)
        grover = Grover(quantum_instance=self.backend)
        result = grover.amplify(problem)
        measured = result.top_measurement
        found = int(measured[::-1], 2)
        return found if search_space[found] == target else -1

    def shor_factorization(self, n: int) -> List[int]:
        """Factor integer ``n`` using Shor's algorithm."""
        if n < 2:
            return []
        if not _QISKIT_AVAILABLE:
            factors = []
            for i in range(2, int(n ** 0.5) + 1):
                if n % i == 0:
                    factors = [i, n // i]
                    break
            return factors or [n]
        shor = Shor(quantum_instance=self.backend)
        result = shor.factorize(n)
        if result.factors:
            return [int(f) for f in result.factors[0]]
        return [n]

    def fourier_transform(self, data: Iterable[complex]) -> List[complex]:
        """Apply the Quantum Fourier Transform to ``data``."""
        data_list = list(data)
        n = self._ensure_power_of_two(len(data_list))
        if not _QISKIT_AVAILABLE:
            return (np.fft.fft(np.array(data_list)) / np.sqrt(len(data_list))).tolist()

        sv = Statevector(data_list)
        qc = QuantumCircuit(n)
        qc.append(QFT(n), range(n))
        transformed = sv.evolve(qc)
        return transformed.data.tolist()
