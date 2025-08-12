"""Simplified quantum annealing routine with simulator/hardware support.

The module is a stopgap and will migrate to a D-Wave backed implementation
once hardware access is approved (planned 2026)."""

from __future__ import annotations

PLACEHOLDER_ONLY = True

from typing import Sequence, Dict

from ghc_quantum.utils.backend_provider import get_backend
from ghc_quantum.utils.audit_log import log_quantum_audit
from . import ensure_not_production

try:  # pragma: no cover - optional dependency
    from qiskit import QuantumCircuit, transpile
    QISKIT_AVAILABLE = True
except Exception:  # pragma: no cover
    QISKIT_AVAILABLE = False


def run_quantum_annealing(cost_vector: Sequence[float], *, use_hardware: bool = False) -> Dict[str, int]:
    """Run a toy quantum annealing routine."""
    ensure_not_production()
    backend = get_backend(use_hardware=use_hardware) if QISKIT_AVAILABLE else None
    n = len(cost_vector)
    if backend is not None:
        qc = QuantumCircuit(n, n)
        for idx, weight in enumerate(cost_vector):
            if weight < 0:
                qc.x(idx)
        qc.measure(range(n)[::-1], range(n))
        compiled = transpile(qc, backend)
        result = backend.run(compiled, shots=1024).result()
        counts = result.get_counts()
    else:
        bitstring = "".join("1" if w < 0 else "0" for w in cost_vector)
        counts = {bitstring: 1024}
    log_quantum_audit("quantum_annealing", list(cost_vector), counts)
    return counts
