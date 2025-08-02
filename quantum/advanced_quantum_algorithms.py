"""Advanced quantum algorithm implementations using Qiskit.

This module provides reference implementations of Grover's search and
quantum phase estimation using the :mod:`qiskit` library.  The
implementations are intentionally lightweight so that they can be used
in unit tests without requiring external services.
"""

from __future__ import annotations

import math

try:  # pragma: no cover - qiskit optional at runtime
    from qiskit import QuantumCircuit, transpile
    from qiskit.circuit.library import QFT
    from qiskit_aer import Aer
    QISKIT_AVAILABLE = True
except Exception:  # pragma: no cover - qiskit optional
    QISKIT_AVAILABLE = False


def grover_search_qiskit(target: str = "11") -> str:
    """Run Grover's search for ``target`` bitstring.

    Parameters
    ----------
    target:
        Bitstring to mark as the correct answer.  The length of the
        string determines the number of search qubits.

    Returns
    -------
    str
        The bitstring measured by the algorithm.
    """

    if not QISKIT_AVAILABLE:  # pragma: no cover - exercised in tests
        raise RuntimeError("qiskit is required for grover_search_qiskit")

    n = len(target)
    qc = QuantumCircuit(n + 1, n)

    # Initial superposition
    qc.h(range(n))
    qc.x(n)
    qc.h(n)

    # Oracle marking the target state
    for i, bit in enumerate(target):
        if bit == "0":
            qc.x(i)
    qc.mcx(list(range(n)), n)
    for i, bit in enumerate(target):
        if bit == "0":
            qc.x(i)

    # Diffusion operator
    qc.h(range(n))
    qc.x(range(n))
    qc.h(n - 1)
    qc.mcx(list(range(n - 1)), n - 1)
    qc.h(n - 1)
    qc.x(range(n))
    qc.h(range(n))

    qc.measure(range(n), range(n))
    backend = Aer.get_backend("qasm_simulator")
    job = backend.run(transpile(qc, backend), shots=1, memory=True)
    counts = job.result().get_counts()
    return max(counts, key=counts.get)


def phase_estimation_qiskit(theta: float, precision: int = 3) -> float:
    """Estimate the phase ``theta`` of a phase gate.

    The unitary whose phase is estimated is ``U = diag(1, e^{2πiθ})``.

    Parameters
    ----------
    theta:
        The phase to estimate, in turns (``1`` == full rotation).
    precision:
        Number of evaluation qubits used in the estimation.

    Returns
    -------
    float
        Estimated phase in turns.
    """

    if not QISKIT_AVAILABLE:  # pragma: no cover - exercised in tests
        raise RuntimeError("qiskit is required for phase_estimation_qiskit")

    qc = QuantumCircuit(precision + 1, precision)
    qc.x(precision)  # eigenstate |1> of phase gate

    for qubit in range(precision):
        qc.h(qubit)
        angle = 2 * math.pi * theta * (2**qubit)
        qc.cp(angle, qubit, precision)

    qc.append(QFT(num_qubits=precision, inverse=True), range(precision))
    qc.measure(range(precision), range(precision))
    backend = Aer.get_backend("qasm_simulator")
    job = backend.run(transpile(qc, backend), shots=1, memory=True)
    counts = job.result().get_counts()
    measured = max(counts, key=counts.get)
    return int(measured, 2) / (2**precision)


__all__ = ["grover_search_qiskit", "phase_estimation_qiskit"]
