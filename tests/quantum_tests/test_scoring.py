import sqlite3
import numpy as np
import quantum_algorithm_library_expansion as qal


class _DummyBackend:
    class _Result:
        def get_counts(self, *_, **__):
            """Return fixed counts regardless of inputs."""
            return {"1": 128}

    def run(self, circ, shots=256):  # pragma: no cover - simple stub
        class _Job:
            def result(self_inner):
                return _DummyBackend._Result()

        return _Job()


def test_quantum_text_score_qiskit(tmp_path, monkeypatch):
    db = tmp_path / "analytics.db"
    qal.ANALYTICS_DB = db
    db.touch()
    qal.QISKIT_AVAILABLE = True
    monkeypatch.setattr(qal, "get_backend", lambda *_, **__: _DummyBackend())
    score = qal.quantum_text_score("hello")
    assert 0 <= score <= 1
    with sqlite3.connect(db) as conn:
        detail = conn.execute("SELECT details FROM quantum_events ORDER BY ROWID DESC LIMIT 1").fetchone()[0]
    assert detail == "qiskit"


def test_quantum_text_score_simulated(tmp_path, monkeypatch):
    db = tmp_path / "analytics.db"
    qal.ANALYTICS_DB = db
    db.touch()
    monkeypatch.setattr(qal, "QISKIT_AVAILABLE", False)
    score = qal.quantum_text_score("hello")
    assert 0 <= score <= 1
    with sqlite3.connect(db) as conn:
        detail = conn.execute("SELECT details FROM quantum_events ORDER BY ROWID DESC LIMIT 1").fetchone()[0]
    assert detail == "simulated"


def test_quantum_text_score_use_hardware_flag(tmp_path, monkeypatch):
    db = tmp_path / "analytics.db"
    qal.ANALYTICS_DB = db
    db.touch()
    qal.QISKIT_AVAILABLE = True
    called = {}

    def _fake_backend(*_, use_hardware=None, **__):
        called["flag"] = use_hardware
        return _DummyBackend()

    monkeypatch.setattr(qal, "get_backend", _fake_backend)
    score = qal.quantum_text_score("hi", use_hardware=True)
    assert called.get("flag") is True
    assert 0 <= score <= 1
    with sqlite3.connect(db) as conn:
        detail = conn.execute("SELECT details FROM quantum_events ORDER BY ROWID DESC LIMIT 1").fetchone()[0]
    assert detail == "qiskit"


def test_quantum_text_score_backend_none_fallback(tmp_path, monkeypatch):
    db = tmp_path / "analytics.db"
    qal.ANALYTICS_DB = db
    db.touch()
    qal.QISKIT_AVAILABLE = True
    monkeypatch.setattr(qal, "get_backend", lambda *_, **__: None)
    score = qal.quantum_text_score("hi", use_hardware=True)
    assert 0 <= score <= 1
    with sqlite3.connect(db) as conn:
        detail = conn.execute("SELECT details FROM quantum_events ORDER BY ROWID DESC LIMIT 1").fetchone()[0]
    assert detail == "simulated"


def test_quantum_similarity_and_cluster_scores(tmp_path):
    db = tmp_path / "analytics.db"
    qal.ANALYTICS_DB = db
    db.touch()
    sim = qal.quantum_similarity_score([1, 0], [0, 1])
    assert 0 <= sim <= 1
    c_score = qal.quantum_cluster_score(np.array([[1.0, 0.0], [0.0, 1.0]]))
    assert isinstance(c_score, float)
    with sqlite3.connect(db) as conn:
        rows = conn.execute("SELECT name FROM quantum_events").fetchall()
    names = [r[0] for r in rows]
    assert "similarity_score" in names
    assert "cluster_score" in names
