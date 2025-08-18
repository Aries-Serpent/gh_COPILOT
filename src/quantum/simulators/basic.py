"""Minimal deterministic quantum simulator.

This stub emulates circuit execution with a trivial all-zero measurement model.
Refer to ``docs/quantum_integration.md`` for full setup and integration details.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Sequence, Tuple

from .base import QuantumSimulator


class BasicSimulator(QuantumSimulator):
    """Simple simulator returning all-zero bitstring counts.

    Parameters
    ----------
    shots:
        Number of measurement shots.
    seed:
        Optional seed for deterministic behaviour. Stored for API compatibility
        but not used in the current stub implementation.
    """

    def __init__(self, shots: int = 1024, seed: Optional[int] = None) -> None:
        self.shots = shots
        self.seed = seed
        # cache of results keyed by (qubit_count, shots)
        self._cache: Dict[Tuple[int, int], Dict[str, int]] = {}

    def run(
        self,
        circuit: Any,
        *,
        shots: Optional[int] = None,
        seed: Optional[int] = None,
        **_: Any,
    ) -> Dict[str, Any]:
        """Simulate ``circuit`` using a deterministic model.

        Each element in ``circuit`` is treated as a qubit initialized to ``|0>``.
        The simulator returns a single measurement outcome consisting entirely of
        zeros with ``shots`` counts. Extra keyword arguments are ignored to
        maintain compatibility with hardware backends. ``seed`` is accepted for
        interface completeness but has no effect.

        See ``docs/quantum_integration.md`` for integration guidance.
        """
        qubits = list(circuit) if isinstance(circuit, Sequence) else [circuit]
        shot_count = self.shots if shots is None else shots
        key = (len(qubits), shot_count)
        if key not in self._cache:
            zeros = "0" * len(qubits)
            self._cache[key] = {zeros: shot_count}
        # return a copy to prevent accidental mutation of cache
        return dict(self._cache[key])
