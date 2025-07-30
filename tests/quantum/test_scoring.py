import sqlite3
import numpy as np
import quantum_algorithm_library_expansion as qal


def test_quantum_text_score_qiskit(tmp_path):
    db = tmp_path / "analytics.db"
    qal.ANALYTICS_DB = db
    db.touch()
    qal.QISKIT_AVAILABLE = True
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
