"""Provider for the built-in simulator backend."""

from __future__ import annotations

from .base import BackendProvider
from quantum.framework.backend import SimulatorBackend


class SimulatorProvider(BackendProvider):
    """Always-available provider that returns :class:`SimulatorBackend`."""

    def get_backend(self) -> SimulatorBackend:
        return SimulatorBackend()

    def is_available(self) -> bool:
        return True


__all__ = ["SimulatorProvider"]

