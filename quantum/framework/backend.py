from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Tuple

from quantum.ibm_backend import init_ibm_backend


class QuantumBackend(ABC):
    """Abstract interface for executing quantum circuits."""

    @abstractmethod
    def run(self, circuit: Any, **kwargs: Any) -> Any:  # pragma: no cover - interface
        """Execute a circuit and return provider specific result."""


class SimulatorBackend(QuantumBackend):
    """Fallback backend that simulates circuit execution."""

    def run(self, circuit: Any, **kwargs: Any) -> dict[str, Any]:
        return {"simulated": True, "circuit": str(circuit)}


def get_backend(token: str | None = None) -> Tuple[QuantumBackend, bool]:
    """Return best available backend with hardware detection.

    Parameters
    ----------
    token:
        Optional IBM token passed through to :func:`init_ibm_backend`.

    Returns
    -------
    tuple
        ``(backend, use_hardware)`` where ``backend`` implements
        :class:`QuantumBackend` and ``use_hardware`` indicates whether a real
        device will be used.
    """
    backend, use_hardware = init_ibm_backend(token=token)
    if backend is None:
        return SimulatorBackend(), False
    if hasattr(backend, "run"):
        # Wrap existing provider object in an adapter so `run` can be called.
        class _Adapter(QuantumBackend):  # pragma: no cover - thin wrapper
            def run(self, circuit: Any, **kwargs: Any) -> Any:
                job = backend.run(circuit, **kwargs)
                return job.result() if hasattr(job, "result") else job

        return _Adapter(), use_hardware
    return SimulatorBackend(), False
