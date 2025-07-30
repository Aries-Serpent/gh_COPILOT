from __future__ import annotations

"""Minimal fallback implementations for QuantumCircuit dependencies."""

from collections import namedtuple


class CircuitData(list):
    """Simplified list-based storage for circuit instructions."""


class _StandardGateMeta(type):
    def __getattr__(cls, name: str):
        return name


class StandardGate(metaclass=_StandardGateMeta):
    HGate = "h"
    CHGate = "ch"
    XGate = "x"
    CXGate = "cx"
    YGate = "y"
    ZGate = "z"
    CZGate = "cz"
    SwapGate = "swap"


CircuitInstruction = namedtuple("CircuitInstruction", ["operation", "qubits", "clbits"])
