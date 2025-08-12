"""IBM Quantum backend provider."""

from __future__ import annotations

import os
import warnings
from typing import Any

from .base import BackendProvider
from quantum.framework.backend import QuantumBackend, SimulatorBackend

try:  # pragma: no cover - optional dependency
    from qiskit_ibm_provider import IBMProvider  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    IBMProvider = None  # type: ignore


try:  # pragma: no cover - optional dependency
    from qiskit import Aer  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    Aer = None  # type: ignore


class IBMBackendProvider(BackendProvider):
    """Provide access to IBM Quantum hardware when available."""

    def __init__(self) -> None:
        self._backend: QuantumBackend | None = None

    def is_available(self) -> bool:
        token = os.getenv("QISKIT_IBM_TOKEN")
        return IBMProvider is not None and token is not None

    def _build_backend(self) -> QuantumBackend:
        token = os.getenv("QISKIT_IBM_TOKEN")
        backend_name = os.getenv("IBM_BACKEND")
        if not self.is_available():
            return SimulatorBackend()
        try:
            provider = IBMProvider(token=token)
            if backend_name:
                backend = provider.get_backend(backend_name)
            else:
                hardware = provider.backends(simulator=False, operational=True)
                backend = hardware[0] if hardware else provider.get_backend("aer_simulator")

            class _Adapter(QuantumBackend):  # pragma: no cover - thin wrapper
                def run(self, circuit: Any, **kwargs: Any) -> Any:
                    job = backend.run(circuit, **kwargs)
                    return job.result() if hasattr(job, "result") else job

            return _Adapter()
        except Exception as exc:  # pragma: no cover - provider issues
            warnings.warn(f"IBM backend unavailable: {exc}; using simulator")
            return SimulatorBackend()

    def get_backend(self) -> QuantumBackend:
        if self._backend is None:
            self._backend = self._build_backend()
        return self._backend


__all__ = ["IBMBackendProvider"]

