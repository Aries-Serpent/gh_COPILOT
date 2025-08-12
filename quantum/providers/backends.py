"""Abstract backend interfaces and provider stubs.

These lightweight classes allow the orchestrator to construct placeholder
backends for various quantum providers without depending on their SDKs.  The
stubs implement :class:`~quantum.framework.backend.QuantumBackend` so tests can
exercise provider selection logic even when hardware libraries are absent.
"""

from __future__ import annotations

from abc import ABC
from typing import Any

from quantum.framework.backend import QuantumBackend


class ProviderBackend(QuantumBackend, ABC):
    """Common interface for provider-specific backends."""


class IBMBackend(ProviderBackend):
    """Stub backend for IBM Quantum."""

    def run(self, circuit: Any, **kwargs: Any) -> dict[str, Any]:
        return {"provider": "ibm", "stub": True, "circuit": str(circuit)}


class IonQBackend(ProviderBackend):
    """Stub backend for IonQ."""

    def run(self, circuit: Any, **kwargs: Any) -> dict[str, Any]:
        return {"provider": "ionq", "stub": True, "circuit": str(circuit)}


class DWaveBackend(ProviderBackend):
    """Stub backend for D-Wave."""

    def run(self, circuit: Any, **kwargs: Any) -> dict[str, Any]:
        return {"provider": "dwave", "stub": True, "circuit": str(circuit)}


__all__ = ["ProviderBackend", "IBMBackend", "IonQBackend", "DWaveBackend"]

