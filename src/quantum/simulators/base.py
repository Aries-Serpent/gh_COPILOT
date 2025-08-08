from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict


class QuantumSimulator(ABC):
    """Abstract interface for local quantum circuit simulators."""

    @abstractmethod
    def run(self, circuit: Any, **kwargs: Any) -> Dict[str, Any]:  # pragma: no cover - interface
        """Simulate ``circuit`` and return a provider-agnostic result."""
