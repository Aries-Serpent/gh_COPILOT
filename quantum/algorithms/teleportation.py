"""Quantum teleportation demonstration algorithm."""

import os
from pathlib import Path
from typing import Optional

from qiskit import QuantumCircuit

from .base import QuantumAlgorithmBase, TEXT_INDICATORS
from ..utils import get_backend


class QuantumTeleportation(QuantumAlgorithmBase):
    """Teleport the state of one qubit to another using a Bell pair."""

    def __init__(self, workspace_path: Optional[str] = None):
        if workspace_path is None:
            workspace_path = os.getenv("GH_COPILOT_WORKSPACE", str(Path.cwd()))
        super().__init__(workspace_path)
        self.backend = None
        self.use_hardware = False

    def get_algorithm_name(self) -> str:
        return "Quantum Teleportation"

    def set_backend(self, backend, use_hardware: bool = False):
        self.backend = backend
        self.use_hardware = use_hardware

    def execute_algorithm(self) -> bool:
        return self.perform_teleportation()

    def perform_teleportation(self) -> bool:
        """Teleport |1> from qubit 0 to qubit 2."""
        self.logger.info(f"{TEXT_INDICATORS['info']} Running teleportation demo")
        try:
            qc = QuantumCircuit(3, 3)
            qc.x(0)  # prepare |1>
            qc.h(1)
            qc.cx(1, 2)
            qc.cx(0, 1)
            qc.h(0)
            qc.measure(0, 0)
            qc.measure(1, 1)
            qc.cz(1, 2)
            qc.cx(0, 2)
            qc.measure(2, 2)

            backend = self.backend or get_backend(use_hardware=self.use_hardware)
            if backend is None:
                self.logger.error(f"{TEXT_INDICATORS['error']} No backend available")
                return False

            result = backend.run(qc, shots=128).result()
            counts = result.get_counts()
            self.execution_stats["counts"] = counts
            self.logger.info(f"{TEXT_INDICATORS['info']} Counts: {counts}")
            success = counts.get("001", 0) + counts.get("101", 0) > 0
            if success:
                self.logger.info(f"{TEXT_INDICATORS['success']} Teleportation successful")
            else:
                self.logger.info(f"{TEXT_INDICATORS['info']} Teleportation completed with counts: {counts}")
            return success
        except Exception as exc:
            self.logger.error(f"{TEXT_INDICATORS['error']} Teleportation failed: {exc}")
            return False


def main():  # pragma: no cover - CLI entry
    utility = QuantumTeleportation()
    success = utility.execute_utility()
    return 0 if success else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
