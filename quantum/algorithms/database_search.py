"""Quantum database search using Grover's algorithm."""

from __future__ import annotations

import logging
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
from qiskit.circuit.library import PhaseOracle
from qiskit.primitives import Sampler

from qiskit import QuantumCircuit
from qiskit.algorithms import Grover

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

    def get_algorithm_name(self) -> str:
        """Return the algorithm name."""
        return "Quantum Database Search"

    def _load_values(self) -> List[Any]:
        conn = sqlite3.connect(self.database_path)
        cur = conn.cursor()
        cur.execute(f"SELECT {self.column} FROM {self.table}")
        values = [row[0] for row in cur.fetchall()]
        conn.close()
        return values

    def _build_oracle(self, values: List[Any], target: Any) -> PhaseOracle:
        truth_table = ''.join('1' if v == target else '0' for v in values)
        if len(truth_table) == 0:
            raise ValueError("Empty search space")
        return PhaseOracle(truth_table)

    def _quantum_search(self, values: List[Any], target: Any) -> Optional[int]:
        num_qubits = int(np.ceil(np.log2(len(values))))
        padded = values + [values[-1]] * (2 ** num_qubits - len(values))
        oracle = self._build_oracle(padded, target)
        grover = Grover(oracle=oracle, sampler=Sampler())
        result = grover.run()
        bitstring = result.result.top_measurement
        index = int(bitstring, 2)
        if index < len(values) and padded[index] == target:
            return index
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
