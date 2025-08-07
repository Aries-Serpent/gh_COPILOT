"""Core abstractions for quantum backend management."""

from .backend import QuantumBackend, SimulatorBackend, get_backend
from .executor import QuantumExecutor

__all__ = [
    "QuantumBackend",
    "SimulatorBackend",
    "get_backend",
    "QuantumExecutor",
]
