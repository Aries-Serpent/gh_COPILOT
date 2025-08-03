import sqlite3
from pathlib import Path

import pytest

from dashboard import compliance_metrics_updater as cmu


@pytest.fixture()
def analytics_db(tmp_path: Path, monkeypatch) -> Path:
    db = tmp_path / "analytics.db"
    with sqlite3.connect(db) as conn:
        conn.execute(
            "CREATE TABLE todo_fixme_tracking (placeholder_type TEXT, status TEXT)"
        )
        conn.executemany(
            "INSERT INTO todo_fixme_tracking VALUES (?, ?)",
            [("TODO", "open"), ("FIXME", "resolved"), ("TODO", "resolved")],
        )
        conn.execute(
            "CREATE TABLE correction_logs (event TEXT, score REAL, timestamp TEXT)"
        )
        conn.executemany(
            "INSERT INTO correction_logs VALUES ('update', ?, ?)",
            [(0.3, "2024-01-01"), (0.6, "2024-01-02")],
        )
        conn.execute(
            "CREATE TABLE violation_logs (details TEXT, timestamp TEXT)"
        )
        conn.execute(
            "INSERT INTO violation_logs VALUES ('v1', '2024-01-03')"
        )
        conn.execute(
            "CREATE TABLE rollback_logs (target TEXT, backup TEXT, timestamp TEXT)"
        )
        conn.execute(
            "INSERT INTO rollback_logs VALUES ('file', 'bak', '2024-01-03')"
        )
        conn.execute(
            "CREATE TABLE performance_metrics (metric_name TEXT, metric_value REAL)"
        )
        conn.executemany(
            "INSERT INTO performance_metrics VALUES ('query_latency', ?)",
            [(10.0,), (20.0,)],
        )
    monkeypatch.setattr(cmu, "validate_no_recursive_folders", lambda: None)
    monkeypatch.setattr(cmu, "ensure_tables", lambda *a, **k: None)
    monkeypatch.setattr(cmu, "validate_environment_root", lambda: None)
    monkeypatch.setattr(cmu, "insert_event", lambda *a, **k: None)
    monkeypatch.setattr(cmu, "ANALYTICS_DB", db)
    return db


def test_score_trend_and_formula(analytics_db: Path, tmp_path: Path):
    updater = cmu.ComplianceMetricsUpdater(tmp_path, test_mode=True)
    metrics = updater._fetch_compliance_metrics(test_mode=True)
    assert metrics["compliance_trend"] == [0.3, 0.6]
    expected = max(0.0, min(1.0, (2 / 3) - 0.1 - 0.05))
    assert metrics["compliance_score"] == pytest.approx(expected, rel=1e-3)


def test_latency_metric(analytics_db: Path):
    with sqlite3.connect(analytics_db) as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT AVG(metric_value) FROM performance_metrics WHERE metric_name='query_latency'"
        )
        avg = cur.fetchone()[0]
    assert avg == pytest.approx(15.0)
