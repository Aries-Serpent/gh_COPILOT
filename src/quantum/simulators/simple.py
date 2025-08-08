from __future__ import annotations

from typing import Any, Dict, Optional

from .base import QuantumSimulator


class SimpleSimulator(QuantumSimulator):
    """Trivial simulator that echoes the circuit and marks result as simulated."""

    def run(
        self,
        circuit: Any,
        *,
        shots: Optional[int] = None,
        seed: Optional[int] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        return {"simulated": True, "circuit": str(circuit)}
