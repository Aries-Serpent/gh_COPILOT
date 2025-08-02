"""Hardware-aware quantum algorithm using IBM provider when available."""

from __future__ import annotations

import logging
from typing import Optional

from tqdm import tqdm

from .base import QuantumAlgorithmBase
from ..utils.backend_provider import get_backend

try:  # pragma: no cover - optional dependency
    from qiskit import QuantumCircuit, execute
except Exception:  # pragma: no cover - qiskit may be missing
    QuantumCircuit = None  # type: ignore
    execute = None  # type: ignore


class HardwareAwareAlgorithm(QuantumAlgorithmBase):
    """Minimal demo algorithm that selects hardware or simulation backends."""

    def __init__(self, use_hardware: Optional[bool] = None):
        super().__init__()
        self.use_hardware = use_hardware

    def get_algorithm_name(self) -> str:  # pragma: no cover - trivial
        return "hardware_aware_demo"

    def execute_algorithm(self) -> bool:
        if QuantumCircuit is None or execute is None:
            self.logger.warning("Qiskit not available")
            return False

        backend = get_backend(use_hardware=self.use_hardware)
        if backend is None:
            self.logger.warning("No backend available")
            return False

        qc = QuantumCircuit(1)
        qc.h(0)
        qc.measure_all()

        with tqdm(total=1, desc="Hardware-aware execution", unit="job") as bar:
            job = execute(qc, backend, shots=128)
            job.result()
            bar.update(1)

        return True


__all__ = ["HardwareAwareAlgorithm"]

