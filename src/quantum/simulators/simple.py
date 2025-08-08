from __future__ import annotations

from typing import Any, Dict

from .base import QuantumSimulator


class SimpleSimulator(QuantumSimulator):
    """Trivial simulator that echoes the circuit and marks result as simulated."""

    def run(self, circuit: Any, **kwargs: Any) -> Dict[str, Any]:
        return {"simulated": True, "circuit": str(circuit)}
