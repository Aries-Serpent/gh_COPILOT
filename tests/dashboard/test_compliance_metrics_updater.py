import logging
import sqlite3
from datetime import datetime

import pytest

from dashboard import compliance_metrics_updater as cmu
from utils.log_utils import ensure_tables


def _prepare_db(path: str) -> None:
    """Initialize required tables for analytics DB."""
    with sqlite3.connect(path) as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS todo_fixme_tracking (status TEXT, placeholder_type TEXT)"
        )
        conn.execute(
            "INSERT INTO violation_logs (timestamp, details) VALUES (?, ?)",
            (datetime.utcnow().isoformat(), "violation"),
        )
        conn.execute(
            "INSERT INTO rollback_logs (target, timestamp) VALUES (?, ?)",
            ("target", datetime.utcnow().isoformat()),
        )
        conn.execute(
            "INSERT INTO todo_fixme_tracking (status, placeholder_type) VALUES ('resolved', 'type1')"
        )
        conn.execute(
            "INSERT INTO todo_fixme_tracking (status, placeholder_type) VALUES ('open', 'type1')"
        )


def test_violation_and_rollback_counts_affect_composite(tmp_path, monkeypatch):
    db = tmp_path / "analytics.db"
    dash_dir = tmp_path / "dash"
    monkeypatch.setattr(cmu, "ANALYTICS_DB", db)
    monkeypatch.setattr(cmu, "DASHBOARD_DIR", dash_dir)
    monkeypatch.setattr(cmu, "validate_no_recursive_folders", lambda: None)
    monkeypatch.setattr(cmu, "validate_environment_root", lambda: None)
    class DummyCorrectionLoggerRollback:
        def __init__(self, *a, **k):
            pass

        def log_violation(self, *a, **k):
            pass

        def log_change(self, *a, **k):
            pass

    monkeypatch.setattr(cmu, "CorrectionLoggerRollback", DummyCorrectionLoggerRollback)
    ensure_tables(db, ["violation_logs", "rollback_logs", "correction_logs", "event_log"], test_mode=False)
    updater = cmu.ComplianceMetricsUpdater(dash_dir, test_mode=True)
    _prepare_db(str(db))

    metrics = updater._fetch_compliance_metrics(test_mode=True)
    assert metrics["violation_count"] == 1
    assert metrics["rollback_count"] == 1
    assert metrics["score_breakdown"]["violation_penalty"] == 10
    assert metrics["score_breakdown"]["rollback_penalty"] == 5
    assert metrics["composite_score"] == pytest.approx(83.0, rel=1e-3)


def test_warn_when_tables_empty(tmp_path, monkeypatch, caplog):
    db = tmp_path / "analytics.db"
    dash_dir = tmp_path / "dash"
    monkeypatch.setattr(cmu, "ANALYTICS_DB", db)
    monkeypatch.setattr(cmu, "DASHBOARD_DIR", dash_dir)
    monkeypatch.setattr(cmu, "validate_no_recursive_folders", lambda: None)
    monkeypatch.setattr(cmu, "validate_environment_root", lambda: None)
    class DummyCorrectionLoggerRollback:
        def __init__(self, *a, **k):
            pass

        def log_violation(self, *a, **k):
            pass

        def log_change(self, *a, **k):
            pass

    monkeypatch.setattr(cmu, "CorrectionLoggerRollback", DummyCorrectionLoggerRollback)
    ensure_tables(db, ["violation_logs", "rollback_logs", "correction_logs", "event_log"], test_mode=False)
    updater = cmu.ComplianceMetricsUpdater(dash_dir, test_mode=True)
    with sqlite3.connect(db) as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS todo_fixme_tracking (status TEXT, placeholder_type TEXT)"
        )

    with caplog.at_level(logging.WARNING):
        metrics = updater._fetch_compliance_metrics(test_mode=True)

    assert metrics["violation_count"] == 0
    assert metrics["rollback_count"] == 0
    warnings = [r.message for r in caplog.records]
    assert any("violation_logs table has no entries" in m for m in warnings)
    assert any("rollback_logs table has no entries" in m for m in warnings)

