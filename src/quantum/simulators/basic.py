"""Minimal deterministic quantum simulator.

This stub emulates circuit execution with a trivial all-zero measurement model.
Refer to ``docs/quantum_integration.md`` for full setup and integration details.
"""

from __future__ import annotations

from typing import Any, Sequence, Dict

from .base import QuantumSimulator


class BasicSimulator(QuantumSimulator):
    """Simple simulator returning all-zero bitstring counts.

    Parameters
    ----------
    shots:
        Number of measurement shots.
    """

    def __init__(self, shots: int = 1024) -> None:
        self.shots = shots

    def run(self, circuit: Any, **_: Any) -> Dict[str, Any]:
        """Simulate ``circuit`` using a deterministic model.

        Each element in ``circuit`` is treated as a qubit initialized to ``|0>``.
        The simulator returns a single measurement outcome consisting entirely of
        zeros with ``shots`` counts. Extra keyword arguments are ignored to
        maintain compatibility with hardware backends.

        See ``docs/quantum_integration.md`` for integration guidance.
        """
        qubits = list(circuit) if isinstance(circuit, Sequence) else [circuit]
        zeros = "0" * len(qubits)
        return {zeros: self.shots}
