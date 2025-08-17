"""D-Wave backend provider (stub)."""

from __future__ import annotations

import os
import warnings
from typing import Any, TYPE_CHECKING

from .base import BackendProvider
from quantum.feature_flags import DWAVE_HARDWARE_ENABLED

if TYPE_CHECKING:  # pragma: no cover - type checking only
    from quantum.framework.backend import QuantumBackend


class DWaveProvider(BackendProvider):
    """Provide access to D-Wave hardware when credentials are available."""

    def __init__(self) -> None:
        self._backend: "QuantumBackend" | None = None

    def is_available(self) -> bool:
        return DWAVE_HARDWARE_ENABLED and bool(os.getenv("DWAVE_API_TOKEN"))

    def _build_backend(self) -> "QuantumBackend":
        if not self.is_available():
            from quantum.framework.backend import SimulatorBackend

            return SimulatorBackend()
        try:  # pragma: no cover - optional dependency
            from dwave.system import DWaveSampler  # type: ignore
            from quantum.framework.backend import QuantumBackend

            class _Adapter(QuantumBackend):
                def run(self, circuit: Any, **kwargs: Any) -> Any:
                    sampler = DWaveSampler(token=os.getenv("DWAVE_API_TOKEN"), solver=os.getenv("DWAVE_SOLVER"))
                    return sampler.sample_qubo(circuit, **kwargs)

            return _Adapter()
        except Exception as exc:  # pragma: no cover - provider issues
            from quantum.framework.backend import SimulatorBackend

            warnings.warn(f"D-Wave backend unavailable: {exc}; using simulator")
            return SimulatorBackend()

    def get_backend(self) -> "QuantumBackend":
        if self._backend is None:
            self._backend = self._build_backend()
        return self._backend


__all__ = ["DWaveProvider"]

