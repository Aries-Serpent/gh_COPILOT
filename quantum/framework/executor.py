from __future__ import annotations

from typing import Any

from .backend import QuantumBackend, SimulatorBackend, get_backend


class QuantumExecutor:
    """Lightweight executor that delegates to a quantum backend.

    The executor automatically falls back to :class:`SimulatorBackend` when a
    hardware backend is unavailable or raises an error during execution.
    """

    def __init__(self, backend: QuantumBackend | None = None, *, token: str | None = None) -> None:
        if backend is None:
            self.backend, self.use_hardware = get_backend(token)
        else:
            self.backend = backend
            self.use_hardware = not isinstance(backend, SimulatorBackend)

    def run(self, circuit: Any, **kwargs: Any) -> Any:
        """Execute ``circuit`` using the configured backend."""
        try:
            return self.backend.run(circuit, **kwargs)
        except Exception:
            self.backend = SimulatorBackend()
            self.use_hardware = False
            return self.backend.run(circuit, **kwargs)
