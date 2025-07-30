import sqlite3
import quantum_algorithm_library_expansion as qal


def test_quantum_text_score_qiskit(tmp_path):
    db = tmp_path / "analytics.db"
    qal.ANALYTICS_DB = db
    db.touch()
    qal.QISKIT_AVAILABLE = True
    score = qal.quantum_text_score("hello")
    assert 0 <= score <= 1
    with sqlite3.connect(db) as conn:
        detail = conn.execute(
            "SELECT details FROM quantum_events ORDER BY ROWID DESC LIMIT 1"
        ).fetchone()[0]
    assert detail == "qiskit"


def test_quantum_text_score_simulated(tmp_path, monkeypatch):
    db = tmp_path / "analytics.db"
    qal.ANALYTICS_DB = db
    db.touch()
    monkeypatch.setattr(qal, "QISKIT_AVAILABLE", False)
    score = qal.quantum_text_score("hello")
    assert 0 <= score <= 1
    with sqlite3.connect(db) as conn:
        detail = conn.execute(
            "SELECT details FROM quantum_events ORDER BY ROWID DESC LIMIT 1"
        ).fetchone()[0]
    assert detail == "simulated"

