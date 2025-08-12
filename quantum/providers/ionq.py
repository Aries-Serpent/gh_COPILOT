"""IonQ backend provider (stub)."""

from __future__ import annotations

from .base import BackendProvider
from quantum.framework.backend import QuantumBackend


class IonQProvider(BackendProvider):
    """Placeholder provider for IonQ backends."""

    def get_backend(self) -> QuantumBackend:  # pragma: no cover - TODO
        raise NotImplementedError("IonQ provider not implemented yet")

    def is_available(self) -> bool:  # pragma: no cover - TODO
        # TODO: detect IonQ SDK availability
        return False


__all__ = ["IonQProvider"]

