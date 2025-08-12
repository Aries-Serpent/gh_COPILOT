"""Prototype Quantum Phase Estimation demo with simulator fallback."""

from __future__ import annotations

from math import pi

from ghc_quantum.utils.backend_provider import get_backend

try:  # pragma: no cover - optional dependency
    from qiskit import QuantumCircuit, transpile
    from qiskit.circuit.library import QFT
    from qiskit.primitives import Sampler
except Exception:  # pragma: no cover - qiskit may be missing
    QuantumCircuit = transpile = QFT = Sampler = None


def run_phase_estimation_demo(use_hardware: bool = False) -> str | None:
    """Estimate the phase of a ``T`` gate applied to ``|1\rangle``.

    Builds a small phase estimation circuit with three evaluation qubits. When
    ``use_hardware`` is True the function attempts to run on an IBM Quantum
    backend and falls back to the local Aer simulator if hardware is
    unavailable.

    Returns:
        The most frequent phase bitstring (length three) or ``None`` if Qiskit
        is unavailable.
    """

    if QuantumCircuit is None:
        return None

    backend = get_backend(use_hardware=True) if use_hardware else None

    qc = QuantumCircuit(4, 3)
    qc.h(range(3))
    qc.x(3)  # prepare eigenstate |1>
    for k in range(3):
        qc.cp(pi / 4 * (2 ** k), k, 3)
    qc.append(QFT(3, inverse=True), range(3))
    qc.measure(range(3), range(3))

    if backend is not None:
        transpiled = transpile(qc, backend)
        job = backend.run(transpiled, shots=1024)
        counts = job.result().get_counts()
    else:
        sampler = Sampler(options={"shots": 1024})
        quasi = sampler.run(qc).result().quasi_dists[0]
        counts = {format(int(k), "03b"): int(v * 1024) for k, v in quasi.items()}
    return max(counts, key=counts.get)


__all__ = ["run_phase_estimation_demo"]

