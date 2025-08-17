"""Interface definitions for quantum hardware backends.

The classes here provide minimal connection stubs so tests can exercise backend selection logic without requiring vendor SDKs. Real implementations will replace the placeholders once hardware access is available.
"""

from __future__ import annotations

from dataclasses import dataclass


class HardwareBackend:
    """Simple protocol for hardware backend connectors."""

    name: str

    def connect(self) -> str:  # pragma: no cover - interface
        """Return a connection identifier for the backend."""
        raise NotImplementedError


@dataclass
class IBMHardwareBackend(HardwareBackend):
    name: str = "ibm"

    def connect(self) -> str:
        return "ibm:simulator"


@dataclass
class IonQHardwareBackend(HardwareBackend):
    name: str = "ionq"

    def connect(self) -> str:
        return "ionq:simulator"


@dataclass
class DWaveHardwareBackend(HardwareBackend):
    name: str = "dwave"

    def connect(self) -> str:
        return "dwave:simulator"


__all__ = [
    "HardwareBackend",
    "IBMHardwareBackend",
    "IonQHardwareBackend",
    "DWaveHardwareBackend",
]
