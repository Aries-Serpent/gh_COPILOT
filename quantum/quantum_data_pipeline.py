"""Quantum-accelerated data pipeline utilities."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import numpy as np

from .quantum_algorithm_library_expansion import advanced_grover_search, advanced_vqe
from .quantum_database_search import DEFAULT_DB_PATH, quantum_join_sql


class QuantumDataPipeline:
    """Simple pipeline combining database joins and algorithm execution."""

    def __init__(self, *, use_hardware: bool = False, backend_name: str | None = None) -> None:
        self.use_hardware = use_hardware
        self.backend_name = backend_name

    def run(self, db_path: str | Path | None = None) -> Dict[str, Any]:
        """Execute the pipeline against ``db_path`` and return results."""

        db = Path(db_path) if db_path else DEFAULT_DB_PATH
        join_results = quantum_join_sql(
            "a",
            "b",
            "l.id = r.id",
            db_path=db,
            use_hardware=self.use_hardware,
            backend_name=self.backend_name,
        )
        grover_result = advanced_grover_search(
            target=1,
            n_qubits=2,
            use_hardware=self.use_hardware,
            backend_name=self.backend_name,
        )
        hamiltonian = np.array([[1, 0], [0, -1]], dtype=float)
        vqe_result = advanced_vqe(
            hamiltonian,
            steps=10,
            use_hardware=self.use_hardware,
            backend_name=self.backend_name,
        )
        return {"join": join_results, "grover": grover_result, "vqe": vqe_result}


__all__ = ["QuantumDataPipeline"]

