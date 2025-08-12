import sqlite3

from ghc_quantum import quantum_database_search as qdb


class DummyCircuit:
    def __init__(self, *args, **kwargs):
        pass

    def h(self, *_):
        pass

    def measure(self, *_):
        pass


class DummyBackend:
    def run(self, *_args, **_kwargs):
        class Result:
            def result(self):
                return None

        return Result()


class DummyProvider:
    def __init__(self, token=None):
        self.token = token

    def get_backend(self, name):
        return DummyBackend()


def test_quantum_search_sql_token_forward(monkeypatch, tmp_path):
    captured = {}

    def provider_factory(token=None):
        captured["token"] = token
        return DummyProvider(token)
    import sys
    import types

    monkeypatch.setitem(
        sys.modules,
        "qiskit_ibm_provider",
        types.SimpleNamespace(IBMProvider=provider_factory),
    )
    monkeypatch.setitem(
        sys.modules,
        "qiskit",
        types.SimpleNamespace(QuantumCircuit=DummyCircuit),
    )
    monkeypatch.setenv("QUANTUM_DB_PATH", str(tmp_path / "log.db"))

    db = tmp_path / "db.sqlite"
    conn = sqlite3.connect(db)
    conn.execute("CREATE TABLE items(x INTEGER)")
    conn.execute("INSERT INTO items VALUES (1)")
    conn.commit()
    conn.close()

    qdb.quantum_search_sql(
        "SELECT x FROM items",
        db_path=db,
        use_hardware=True,
        backend_name="dummy",
        token="tok",
    )

    assert captured["token"] == "tok"
