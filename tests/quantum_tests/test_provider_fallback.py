import builtins
import sqlite3
from pathlib import Path

from ghc_quantum.orchestration.executor import QuantumExecutor
from ghc_quantum.orchestration import executor as qexec
from ghc_quantum.orchestration.registry import register_algorithm
from ghc_quantum.algorithms.base import QuantumAlgorithmBase
from ghc_quantum.quantum_database_search import quantum_search_sql


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
    monkeypatch.setattr(
        qexec, "init_ibm_backend", lambda token=None, backend_name=None: (None, False)
    )
    exec_ = QuantumExecutor(use_hardware=True)
    assert exec_.use_hardware is False
    if qexec.QISKIT_AVAILABLE:
        assert exec_.backend is not None
    else:
        assert exec_.backend is None
    result = exec_.execute_algorithm("dummy_fallback")
    assert result["success"]


def test_quantum_search_sql_fallback(tmp_path, monkeypatch):
    db = tmp_path / "db.sqlite"
    _setup_db(db)
    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "qiskit_ibm_provider":
            raise ImportError("no provider")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    results = quantum_search_sql(
        "SELECT name FROM items", db, use_hardware=True, backend_name="mock"
    )
    assert {"name": "a"} in results and {"name": "b"} in results
