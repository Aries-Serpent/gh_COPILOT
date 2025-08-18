from __future__ import annotations

from abc import ABC, abstractmethod
import random
from typing import Any


class QuantumBackend(ABC):
    """Abstract interface for executing quantum circuits."""

    @abstractmethod
    def run(self, circuit: Any, **kwargs: Any) -> Any:  # pragma: no cover - interface
        """Execute a circuit and return provider specific result."""


class SimulatorBackend(QuantumBackend):
    """Fallback backend that simulates circuit execution.

    The simulator accepts an optional ``seed`` argument to ensure
    deterministic results across runs which is important for unit tests
    and reproducibility.
    """

    def run(
        self,
        circuit: Any,
        *,
        seed: int | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        rng = random.Random(seed)
        value = rng.random()
        return {"simulated": True, "circuit": str(circuit), "value": value}



