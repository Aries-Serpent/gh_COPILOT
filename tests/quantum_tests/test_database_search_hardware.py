"""Integration tests for QuantumDatabaseSearch hardware execution."""

import sqlite3

import pytest

from ghc_quantum.algorithms.database_search import QuantumDatabaseSearch


class DummyBackend:
    def __init__(self):
        self.called = False

    def run(self, *_args, **_kwargs):
        self.called = True

        class _Result:
            def result(self):  # pragma: no cover - simple container
                class _Counts:
                    def get_counts(self):
                        return {"01": 1024}

                return _Counts()

        return _Result()


def test_hardware_path_invoked(monkeypatch, tmp_path):
    pytest.importorskip("qiskit")

    db = tmp_path / "db.sqlite"
    conn = sqlite3.connect(db)
    conn.execute("CREATE TABLE items(val INTEGER)")
    conn.executemany("INSERT INTO items VALUES (?)", [(1,), (2,)])
    conn.commit()
    conn.close()

    algo = QuantumDatabaseSearch(str(db), "items", "val")
    backend = DummyBackend()
    algo.set_backend(backend, use_hardware=True)

    assert algo.execute_algorithm(2)
    assert backend.called

