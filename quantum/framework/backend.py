from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class QuantumBackend(ABC):
    """Abstract interface for executing quantum circuits."""

    @abstractmethod
    def run(self, circuit: Any, **kwargs: Any) -> Any:  # pragma: no cover - interface
        """Execute a circuit and return provider specific result."""


class SimulatorBackend(QuantumBackend):
    """Fallback backend that simulates circuit execution."""

    def run(self, circuit: Any, **kwargs: Any) -> dict[str, Any]:
        return {"simulated": True, "circuit": str(circuit)}



