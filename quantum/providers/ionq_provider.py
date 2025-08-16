"""IonQ backend provider (stub)."""

from __future__ import annotations

import os
import warnings
from typing import Any, TYPE_CHECKING

from .base import BackendProvider
from quantum.feature_flags import IONQ_HARDWARE_ENABLED

if TYPE_CHECKING:  # pragma: no cover - type checking only
    from quantum.framework.backend import QuantumBackend


try:  # pragma: no cover - optional dependency
    from qiskit_ionq import IonQProvider as _IonQProvider  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    _IonQProvider = None  # type: ignore


class IonQProvider(BackendProvider):
    """Provide access to IonQ hardware when the SDK is installed."""

    def __init__(self) -> None:
        self._backend: "QuantumBackend" | None = None

    def is_available(self) -> bool:
        """Return ``True`` when the IonQ SDK and credentials are present."""

        return (
            IONQ_HARDWARE_ENABLED
            and _IonQProvider is not None
            and bool(os.getenv("IONQ_API_KEY"))
        )

    def _build_backend(self) -> "QuantumBackend":
        api_key = os.getenv("IONQ_API_KEY")
        backend_name = os.getenv("IONQ_BACKEND")
        if not self.is_available():
            from quantum.framework.backend import SimulatorBackend

            return SimulatorBackend()
        try:
            provider = _IonQProvider(api_key=api_key)
            if backend_name:
                backend = provider.get_backend(backend_name)
            else:
                hardware = provider.backends(simulator=False)
                backend = hardware[0] if hardware else provider.get_backend("ionq.simulator")

            class _Adapter(QuantumBackend):  # pragma: no cover - thin wrapper
                def run(self, circuit: Any, **kwargs: Any) -> Any:
                    job = backend.run(circuit, **kwargs)
                    return job.result() if hasattr(job, "result") else job

            return _Adapter()
        except Exception as exc:  # pragma: no cover - provider issues
            from quantum.framework.backend import SimulatorBackend

            warnings.warn(f"IonQ backend unavailable: {exc}; using simulator")
            return SimulatorBackend()

    def get_backend(self) -> "QuantumBackend":
        if self._backend is None:
            self._backend = self._build_backend()
        return self._backend


__all__ = ["IonQProvider"]

