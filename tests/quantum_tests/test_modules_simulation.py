import sqlite3
from pathlib import Path

import numpy as np

from ghc_quantum.quantum_database_search import quantum_search_hybrid, quantum_search_sql
from ghc_quantum.optimizers.quantum_optimizer import QuantumOptimizer


def _setup_db(path: Path) -> None:
    with sqlite3.connect(path) as conn:
        conn.execute("CREATE TABLE items(name TEXT)")
        conn.executemany("INSERT INTO items VALUES (?)", [("a",), ("b",)])

def test_quantum_search_sql_simulation(tmp_path: Path, monkeypatch):
    db = tmp_path / "db.sqlite"
    _setup_db(db)
    monkeypatch.setenv("GH_COPILOT_TEST_MODE", "1")
    results = quantum_search_sql("SELECT name FROM items", db, use_hardware=False)
    assert {"name": "a"} in results and {"name": "b"} in results


def test_quantum_search_hybrid_simulation(tmp_path: Path, monkeypatch):
    db = tmp_path / "db.sqlite"
    _setup_db(db)
    monkeypatch.setenv("GH_COPILOT_TEST_MODE", "1")
    results = quantum_search_hybrid("sql", "SELECT name FROM items", db, use_hardware=False)
    assert len(results) == 2


def test_quantum_optimizer_simulation():
    def obj(x: np.ndarray) -> float:
        return float(np.sum((x - 1) ** 2))

    opt = QuantumOptimizer(obj, [(-2, 2), (-2, 2)], method="simulated_annealing")
    out = opt.run(x0=np.array([0.0, 0.0]), max_iter=5)
    assert "best_result" in out["result"]
    assert isinstance(out["result"]["best_value"], float)
