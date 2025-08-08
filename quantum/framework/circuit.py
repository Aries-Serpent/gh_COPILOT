"""Lightweight circuit container for simulation purposes."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class QuantumCircuit:
    """Minimal representation of a quantum circuit."""

    description: str

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"QuantumCircuit({self.description})"
