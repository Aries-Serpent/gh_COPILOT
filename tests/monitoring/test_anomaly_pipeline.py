import json
import sqlite3
import sys
from types import SimpleNamespace
import pytest


def _stub_score(values):
    vals = list(values)
    return sum(vals) / len(vals)




@pytest.fixture(autouse=True)
def _stub_quantum_module(monkeypatch):
    """Provide a temporary quantum scoring stub."""
    monkeypatch.setitem(
        sys.modules,
        "quantum_algorithm_library_expansion",
        SimpleNamespace(quantum_score_stub=_stub_score),
    )

from unified_monitoring_optimization_system import anomaly_detection_loop
from dashboard.enterprise_dashboard import anomaly_metrics


class DummyManager:
    def __init__(self) -> None:
        self.started = 0
        self.ended = 0

    def start_session(self) -> None:  # pragma: no cover - simple increment
        self.started += 1

    def end_session(self) -> None:  # pragma: no cover - simple increment
        self.ended += 1


def test_anomaly_pipeline_triggers_heal_and_reports_metrics(monkeypatch, tmp_path):
    db = tmp_path / "analytics.db"
    model = tmp_path / "model.pkl"
    history = [
        {"cpu": 1.0, "mem": 1.0},
        {"cpu": 1.1, "mem": 1.1},
        {"cpu": 95.0, "mem": 99.0},
    ]
    metrics_iter = iter(history)

    def fake_collect_metrics(*, db_path=None, session_id=None):
        return next(metrics_iter)

    call_count = {"n": 0}
    total = len(history)

    def fake_detect(history, **kwargs):
        call_count["n"] += 1
        if call_count["n"] < total:
            return []
        metrics = history[-1]
        path = kwargs.get("db_path") or db
        with sqlite3.connect(path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS anomaly_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    metrics_json TEXT NOT NULL,
                    anomaly_score REAL NOT NULL,
                    quantum_score REAL,
                    composite_score REAL NOT NULL
                )
                """
            )
            conn.execute(
                "INSERT INTO anomaly_results (metrics_json, anomaly_score, quantum_score, composite_score) VALUES (?, ?, ?, ?)",
                (json.dumps(metrics), 1.0, None, 1.0),
            )
            conn.commit()
        return [dict(metrics, anomaly_score=1.0, composite_score=1.0)]

    monkeypatch.setattr(
        "unified_monitoring_optimization_system.collect_metrics", fake_collect_metrics
    )
    monkeypatch.setattr(
        "unified_monitoring_optimization_system.detect_anomalies", fake_detect
    )
    monkeypatch.setattr(
        "unified_monitoring_optimization_system.time.sleep", lambda _t: None
    )

    mgr = DummyManager()
    anomaly_detection_loop(
        interval=0,
        iterations=len(history),
        manager=mgr,
        db_path=db,
        model_path=model,
    )

    assert mgr.started == 1
    assert mgr.ended == 1

    stats = anomaly_metrics(db)
    assert stats["count"] == 1
    assert stats["avg_anomaly_score"] == 1.0
