"""Simple quantum model using the simulation framework."""

from __future__ import annotations

from ghc_quantum.framework.circuit import QuantumCircuit
from .base import QuantumModel


class DemoModel(QuantumModel):
    """Trivial quantum model returning a placeholder circuit."""

    def build_circuit(self) -> QuantumCircuit:  # pragma: no cover - trivial
        return QuantumCircuit("demo")
