"""Minimal deterministic quantum simulator.

This stub emulates circuit execution with a trivial all-zero measurement model.
Refer to ``docs/quantum_integration.md`` for full setup and integration details.
"""

from __future__ import annotations

from typing import Any, Sequence


class BasicSimulator:
    """Simple simulator returning all-zero bitstring counts.

    Parameters
    ----------
    shots:
        Number of measurement shots.
    """

    def __init__(self, shots: int = 1024) -> None:
        self.shots = shots

    def run(self, circuit: Sequence[Any]) -> dict[str, int]:
        """Simulate a circuit using a deterministic model.

        Each element in ``circuit`` is treated as a qubit initialized to ``|0>``.
        The simulator returns a single measurement outcome consisting entirely of
        zeros with ``shots`` counts.

        See ``docs/quantum_integration.md`` for integration guidance.
        """
        zeros = "0" * len(list(circuit))
        return {zeros: self.shots}
