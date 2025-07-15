#!/usr/bin/env python3
from __future__ import annotations

import math

<<<<<<< HEAD
import numpy as np_module
from qiskit import QuantumCircuit

try:
    from qiskit.algorithms import Shor
except Exception:  # pragma: no cover - use local stub
    from copilot_qiskit_stubs.algorithms import Shor  # type: ignore
=======
import numpy as np
from qiskit import QuantumCircuit
try:
    from qiskit.algorithms import Shor
except Exception:  # pragma: no cover - use local fallback
    from physics_optimization_engine import Shor  # type: ignore
>>>>>>> 072d1e7e (Nuclear fix: Complete repository rebuild - 2025-07-14 22:31:03)
from qiskit.circuit.library import QFT
from qiskit.quantum_info import Statevector
from qiskit_aer import AerSimulator

<<<<<<< HEAD
from scripts.optimization.physics_optimization_engine import PhysicsOptimizationEngine
=======
from physics_optimization_engine import PhysicsOptimizationEngine
import numpy as np
import logging
>>>>>>> 072d1e7e (Nuclear fix: Complete repository rebuild - 2025-07-14 22:31:03)


def _grover_index(expected_index: int, num_qubits: int) -> int:
    qc = QuantumCircuit(num_qubits, num_qubits)
    qc.h(range(num_qubits))

    def oracle(circ: QuantumCircuit) -> None:
        for q in range(num_qubits):
            if (expected_index >> q) & 1 == 0:
                circ.x(q)
        if num_qubits == 1:
            circ.z(0)
        else:
            circ.h(num_qubits - 1)
            circ.mcx(list(range(num_qubits - 1)), num_qubits - 1)
            circ.h(num_qubits - 1)
        for q in range(num_qubits):
            if (expected_index >> q) & 1 == 0:
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

<<<<<<< HEAD
    iterations = max(1, int(math.pi / 4 * math.sqrt(2**num_qubits)))
=======
    iterations = max(1, int(math.pi / 4 * math.sqrt(2 ** num_qubits)))
>>>>>>> 072d1e7e (Nuclear fix: Complete repository rebuild - 2025-07-14 22:31:03)
    for _ in range(iterations):
        oracle(qc)
        diffusion(qc)

    qc.measure(range(num_qubits), range(num_qubits))
    backend = AerSimulator()
    counts = backend.run(qc, shots=1024).result().get_counts()
    measured = max(counts, key=counts.get)
    return int(measured, 2)


def test_grover_search_found():
    engine = PhysicsOptimizationEngine()
    data = [1, 2, 3, 4]
    result = engine.grover_search(data, 3)
    expected = _grover_index(2, 2)
    assert result == expected == 2


def test_shor_factorization():
    engine = PhysicsOptimizationEngine()
    result = engine.shor_factorization(15)
    backend = AerSimulator()
    expected = Shor(quantum_instance=backend).factor(15).factors[0]
    assert set(result) == set(expected)


def test_fourier_transform():
    engine = PhysicsOptimizationEngine()
    data = [0, 1, 0, -1]
    result = engine.fourier_transform(data)
    qc = QuantumCircuit(2)
    qc.initialize(data, range(2), normalize=True)
    qc.append(QFT(2, do_swaps=False), range(2))
    expected = Statevector.from_instruction(qc).data.tolist()
    assert len(result) == len(expected)
<<<<<<< HEAD
    assert np_module.allclose(result, expected)
=======
    assert np.allclose(result, expected)
>>>>>>> 072d1e7e (Nuclear fix: Complete repository rebuild - 2025-07-14 22:31:03)
