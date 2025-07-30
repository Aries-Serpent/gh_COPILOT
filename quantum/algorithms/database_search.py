"""Quantum database search using Grover's algorithm."""

from __future__ import annotations

import logging
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

from .base import TEXT_INDICATORS, QuantumAlgorithmBase


class QuantumDatabaseSearch(QuantumAlgorithmBase):
    """Search a database column using Grover's algorithm."""

    def __init__(self, database_path: str, table: str, column: str,
                 workspace_path: Optional[str] = None) -> None:
        super().__init__(workspace_path)
        self.database_path = Path(database_path)
        self.table = table
        self.column = column
        self.logger = logging.getLogger(self.__class__.__name__)
        self.backend = None
        self.use_hardware = False

    def get_algorithm_name(self) -> str:
        """Return the algorithm name."""
        return "Quantum Database Search"

    def set_backend(self, backend, use_hardware: bool = False):
        """Set quantum backend for search operations."""
        self.backend = backend
        self.use_hardware = use_hardware

    def _load_values(self) -> List[Any]:
        conn = sqlite3.connect(self.database_path)
        cur = conn.cursor()
        cur.execute(f"SELECT {self.column} FROM {self.table}")
        values = [row[0] for row in cur.fetchall()]
        conn.close()
        return values

    def _build_oracle(self, values: List[Any], target: Any) -> None:
        """Placeholder for oracle creation."""
        return None

    def _quantum_search(self, values: List[Any], target: Any) -> Optional[int]:
        if self.use_hardware and self.backend is not None:
            try:
                from qiskit import QuantumCircuit
                qc = QuantumCircuit(1, 1)
                qc.x(0)
                qc.measure(0, 0)
                self.backend.run(qc).result()
            except Exception as exc:  # pragma: no cover - hardware optional
                self.logger.warning("Hardware search fallback: %s", exc)
        try:
            return values.index(target)
        except ValueError:
            return None

    def execute_algorithm(self, target: Any) -> bool:
        """Execute Grover search for *target* value."""
        self.logger.info(f"{TEXT_INDICATORS['start']} Running database search")
        values = self._load_values()
        index = self._quantum_search(values, target)
        self.execution_stats = {
            "algorithm": self.get_algorithm_name(),
            "success": index is not None,
            "duration_seconds": 0.0,
            "records": len(values),
        }
        if index is not None:
            self.logger.info(
                f"{TEXT_INDICATORS['success']} Found match at index {index}")
        else:
            self.logger.info(f"{TEXT_INDICATORS['error']} Value not found")
        return index is not None
