import sqlite3
from pathlib import Path

from quantum.orchestration.executor import QuantumExecutor
from quantum.orchestration.registry import register_algorithm
from quantum.algorithms.base import QuantumAlgorithmBase
from quantum.quantum_database_search import quantum_search_sql
from quantum.utils import backend_provider


class DummyAlgo(QuantumAlgorithmBase):
    def __init__(self):
        super().__init__(None)

    def get_algorithm_name(self) -> str:
        return "dummy_fallback"

    def execute_algorithm(self) -> bool:
        return True


register_algorithm("dummy_fallback", DummyAlgo)


def _setup_db(path: Path) -> None:
    with sqlite3.connect(path) as conn:
        conn.execute("CREATE TABLE items(name TEXT)")
        conn.executemany("INSERT INTO items VALUES (?)", [("a",), ("b",)])


def test_executor_falls_back_without_ibm(monkeypatch):
    monkeypatch.setattr(backend_provider, "_load_provider", lambda: None)
    exec_ = QuantumExecutor(use_hardware=True)
    assert exec_.use_hardware is False
    if backend_provider.Aer is not None:
        assert exec_.backend is not None
    else:
        assert exec_.backend is None
    result = exec_.execute_algorithm("dummy_fallback")
    assert result["success"]


def test_quantum_search_sql_fallback(tmp_path, monkeypatch):
    db = tmp_path / "db.sqlite"
    _setup_db(db)
    monkeypatch.setattr(backend_provider, "_load_provider", lambda: None)
    results = quantum_search_sql(
        "SELECT name FROM items", db, use_hardware=True, backend_name="mock"
    )
    assert {"name": "a"} in results and {"name": "b"} in results

