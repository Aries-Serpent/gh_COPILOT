"""Quantum-enhanced database processing utilities.

Provides a tiny hybrid processor that demonstrates how the project can
toggle between classical and quantum execution paths. The class exposes a
``process`` method returning which mode was used so callers can verify
fallback behaviour.
"""

from __future__ import annotations

from typing import Any, Dict


class QuantumDatabaseProcessor:
    """Process database queries using quantum or classical resources.

    Parameters
    ----------
    use_quantum:
        Hint that quantum resources should be used when available.
    hardware_available:
        Whether a quantum backend is available. When ``False`` the
        processor automatically falls back to classical processing even if
        ``use_quantum`` is ``True``.
    """

    def __init__(
        self, *, use_quantum: bool = True, hardware_available: bool = False
    ) -> None:
        self.use_quantum = use_quantum
        self.hardware_available = hardware_available

    def process(self, query: str) -> Dict[str, Any]:
        """Process a database query and note which execution path was used."""

        if self.use_quantum and self.hardware_available:
            return {"mode": "quantum", "data": f"quantum_result:{query}"}

        return {"mode": "classical", "data": f"classical_result:{query}"}


__all__ = ["QuantumDatabaseProcessor"]

