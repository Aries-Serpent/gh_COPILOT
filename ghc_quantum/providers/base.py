"""Protocol for quantum backend providers."""

from __future__ import annotations

from typing import Protocol

from ghc_quantum.framework.backend import QuantumBackend


class BackendProvider(Protocol):
    """Interface implemented by all backend providers."""

    def get_backend(self) -> QuantumBackend:  # pragma: no cover - protocol
        """Return a :class:`~ghc_quantum.framework.backend.QuantumBackend` instance."""

    def is_available(self) -> bool:  # pragma: no cover - protocol
        """Return ``True`` if the provider can supply a backend."""


__all__ = ["BackendProvider"]

