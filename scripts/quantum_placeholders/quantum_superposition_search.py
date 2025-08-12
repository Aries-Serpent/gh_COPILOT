"""Uniform superposition generator with optional hardware execution.

Planned promotion to a hardware-backed search routine after the IonQ pilot
completes in late 2025."""

from __future__ import annotations

PLACEHOLDER_ONLY = True

from typing import Dict

from ghc_quantum.utils.backend_provider import get_backend
from ghc_quantum.utils.audit_log import log_quantum_audit
from . import ensure_not_production

try:  # pragma: no cover - optional dependency
    from qiskit import QuantumCircuit, transpile
    QISKIT_AVAILABLE = True
except Exception:  # pragma: no cover
    QISKIT_AVAILABLE = False


def run_quantum_superposition_search(num_qubits: int = 2, *, use_hardware: bool = False) -> Dict[str, float]:
    """Return probability distribution for a uniform superposition."""
    ensure_not_production()
    backend = get_backend(use_hardware=use_hardware) if QISKIT_AVAILABLE else None
    n = num_qubits
    if backend is not None and getattr(backend.configuration(), "simulator", True):
        from qiskit_aer import Aer
        qc = QuantumCircuit(n)
        qc.h(range(n))
        state = Aer.get_backend("statevector_simulator").run(transpile(qc, Aer.get_backend("statevector_simulator"))).result().get_statevector()
        probs = {format(i, f"0{n}b"): float(abs(amp) ** 2) for i, amp in enumerate(state)}
    elif backend is not None:  # pragma: no cover - hardware execution
        qc = QuantumCircuit(n, n)
        qc.h(range(n))
        qc.measure(range(n)[::-1], range(n))
        counts = backend.run(transpile(qc, backend), shots=1024).result().get_counts()
        total = sum(counts.values())
        probs = {k: v / total for k, v in counts.items()}
    else:
        probs = {format(i, f"0{n}b"): 1 / (2 ** n) for i in range(2 ** n)}
    log_quantum_audit("quantum_superposition_search", n, probs)
    return probs
