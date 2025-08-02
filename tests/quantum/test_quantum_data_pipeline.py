import sqlite3

import numpy as np
import pytest

from quantum import (
    QuantumIntegrationOrchestrator,
    advanced_grover_search,
    advanced_vqe,
    quantum_join_sql,
)


def _setup_db(path):
    with sqlite3.connect(path) as conn:
        conn.execute("CREATE TABLE a(id INTEGER PRIMARY KEY, v INTEGER)")
        conn.execute("CREATE TABLE b(id INTEGER PRIMARY KEY, v INTEGER)")
        conn.executemany("INSERT INTO a(id, v) VALUES (?, ?)", [(1, 10), (2, 20)])
        conn.executemany("INSERT INTO b(id, v) VALUES (?, ?)", [(1, 100), (3, 300)])
        conn.commit()


def test_advanced_grover_search_fallback():
    assert advanced_grover_search(1, n_qubits=2) == 1
    assert advanced_grover_search(1, n_qubits=2, use_hardware=True) == 1


def test_advanced_vqe_fallback():
    h = np.array([[1, 0], [0, -1]], dtype=float)
    sim = advanced_vqe(h, steps=5)
    hw = advanced_vqe(h, steps=5, use_hardware=True)
    assert pytest.approx(sim["energy"], rel=1e-6) == hw["energy"]


def test_quantum_join_sql(tmp_path):
    db = tmp_path / "test.db"
    _setup_db(db)
    rows = quantum_join_sql("a", "b", "l.id = r.id", db_path=db)
    assert rows == [{"id": 1, "left_v": 10, "right_v": 100}]


def test_quantum_data_pipeline(tmp_path):
    db = tmp_path / "pipeline.db"
    _setup_db(db)
    orchestrator = QuantumIntegrationOrchestrator(use_hardware=True)
    result = orchestrator.run_data_pipeline(db_path=db)
    assert result["join"] == [{"id": 1, "left_v": 10, "right_v": 100}]
    assert result["grover"] == 1
    assert "energy" in result["vqe"]

