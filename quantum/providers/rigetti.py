"""Rigetti backend provider (stub)."""

from __future__ import annotations

from .base import BackendProvider
from quantum.framework.backend import QuantumBackend


class RigettiProvider(BackendProvider):
    """Placeholder provider for Rigetti backends."""

    def get_backend(self) -> QuantumBackend:  # pragma: no cover - TODO
        raise NotImplementedError("Rigetti provider not implemented yet")

    def is_available(self) -> bool:  # pragma: no cover - TODO
        # TODO: detect Rigetti SDK availability
        return False


__all__ = ["RigettiProvider"]

