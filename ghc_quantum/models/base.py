from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from ghc_quantum.framework import QuantumExecutor


class QuantumModel(ABC):
    """Base class for quantum-enabled models."""

    def __init__(self, executor: QuantumExecutor | None = None) -> None:
        self.executor = executor or QuantumExecutor()

    @abstractmethod
    def build_circuit(self) -> Any:  # pragma: no cover - interface
        """Construct a circuit representation."""

    def run(self, **kwargs: Any) -> Any:
        """Build and execute the model's circuit."""
        circuit = self.build_circuit()
        return self.executor.run(circuit, **kwargs)
