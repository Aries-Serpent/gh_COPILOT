from __future__ import annotations

import os
from typing import Any

from .backend import QuantumBackend, SimulatorBackend
from quantum.feature_flags import is_quantum_enabled
from quantum.providers import get_provider


class QuantumExecutor:
    """Lightweight executor that delegates to a quantum backend.

    The executor automatically falls back to :class:`SimulatorBackend` when a
    hardware backend is unavailable or raises an error during execution.
    """

    def __init__(self, backend: QuantumBackend | None = None, *, provider: str | None = None) -> None:
        if backend is not None:
            self.backend = backend
            self.use_hardware = not isinstance(backend, SimulatorBackend)
            return

        if os.getenv("ENABLE_QUANTUM_PROVIDERS", "1") != "1":
            self.backend = SimulatorBackend()
            self.use_hardware = False
            return

        provider_name = provider or os.getenv("QUANTUM_PROVIDER", "simulator")
        prov = get_provider(provider_name)
        if not prov.is_available():
            prov = get_provider("simulator")
            self.use_hardware = False
        else:
            self.use_hardware = provider_name != "simulator"
        self.backend = prov.get_backend()

    def run(self, circuit: Any, **kwargs: Any) -> Any:
        """Execute ``circuit`` using the configured backend."""
        if not is_quantum_enabled():
            raise RuntimeError("Quantum execution disabled")
        if self.use_hardware and os.getenv("QISKIT_IBM_TOKEN") is None:
            raise RuntimeError("QISKIT_IBM_TOKEN not set")

        seed = kwargs.pop("seed", None)
        try:
            return self.backend.run(circuit, seed=seed, **kwargs)
        except Exception:
            self.backend = SimulatorBackend()
            self.use_hardware = False
            return self.backend.run(circuit, seed=seed, **kwargs)
