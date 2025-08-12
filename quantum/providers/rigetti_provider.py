"""Rigetti backend provider."""

from __future__ import annotations

import os
import warnings
from typing import Any

from .base import BackendProvider
from quantum.framework.backend import QuantumBackend, SimulatorBackend

try:  # pragma: no cover - optional dependency
    from pyquil.api import WavefunctionSimulator  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    WavefunctionSimulator = None  # type: ignore


class RigettiProvider(BackendProvider):
    """Provide access to Rigetti backends via the `pyquil` SDK.

    The provider checks for the presence of the Rigetti SDK and two
    environment variables:

    - ``RIGETTI_API_KEY`` – API key for authentication.
    - ``RIGETTI_CLUSTER_URL`` – URL of the target cluster.

    If the SDK or required environment variables are missing, a
    :class:`~quantum.framework.backend.SimulatorBackend` is returned
    instead.
    """

    def __init__(self) -> None:
        self._backend: QuantumBackend | None = None

    def is_available(self) -> bool:
        """Return ``True`` when the Rigetti SDK and credentials are present."""

        return (
            WavefunctionSimulator is not None
            and os.getenv("RIGETTI_API_KEY") is not None
            and os.getenv("RIGETTI_CLUSTER_URL") is not None
        )

    def _build_backend(self) -> QuantumBackend:
        if not self.is_available():
            return SimulatorBackend()

        try:
            simulator = WavefunctionSimulator()

            class _RigettiBackend(QuantumBackend):  # pragma: no cover - thin wrapper
                def run(self, circuit: Any, **kwargs: Any) -> Any:
                    return simulator.wavefunction(circuit, **kwargs).amplitudes

            return _RigettiBackend()
        except Exception as exc:  # pragma: no cover - provider issues
            warnings.warn(f"Rigetti backend unavailable: {exc}; using simulator")
            return SimulatorBackend()

    def get_backend(self) -> QuantumBackend:
        if self._backend is None:
            self._backend = self._build_backend()
        return self._backend


__all__ = ["RigettiProvider"]
