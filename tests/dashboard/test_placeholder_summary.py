import json
import sqlite3
import sys
import types
from pathlib import Path

import pytest

# Stub problematic dependency before importing module
sys.modules.setdefault(
    "scripts.correction_logger_and_rollback",
    types.SimpleNamespace(
        CorrectionLoggerRollback=type(
            "_Stub",
            (),
            {
                "__init__": lambda self, *a, **k: None,
                "log_violation": lambda self, *a, **k: None,
                "log_change": lambda self, *a, **k: None,
            },
        )
    ),
)
from dashboard import compliance_metrics_updater as cmu


@pytest.fixture()
def updater(tmp_path: Path, monkeypatch):
    db = tmp_path / "analytics.db"
    with sqlite3.connect(db) as conn:
        conn.execute(
            "CREATE TABLE todo_fixme_tracking (placeholder_type TEXT, status TEXT)"
        )
        conn.execute("INSERT INTO todo_fixme_tracking VALUES ('TODO', 'open')")
        conn.execute(
            "CREATE TABLE correction_logs (event TEXT, score REAL, timestamp TEXT)"
        )
        conn.execute("INSERT INTO correction_logs VALUES ('update', 0.1, '2024-01-01')")
        conn.execute(
            "CREATE TABLE violation_logs (details TEXT, timestamp TEXT)"
        )
        conn.execute(
            "CREATE TABLE rollback_logs (target TEXT, backup TEXT, timestamp TEXT)"
        )
    monkeypatch.setattr(cmu, "validate_no_recursive_folders", lambda: None)
    monkeypatch.setattr(cmu, "ensure_tables", lambda *a, **k: None)
    monkeypatch.setattr(cmu, "validate_environment_root", lambda: None)
    monkeypatch.setattr(cmu, "insert_event", lambda *a, **k: None)
    monkeypatch.setattr(cmu, "ANALYTICS_DB", db)
    monkeypatch.setattr(
        cmu.ComplianceMetricsUpdater,
        "_sync_external_systems",
        lambda self, metrics: None,
        raising=False,
    )
    updater = cmu.ComplianceMetricsUpdater(tmp_path, test_mode=True)
    return updater, tmp_path


def test_placeholder_summary_created(updater):
    updater_obj, path = updater
    updater_obj.update()
    summary = path / "placeholder_summary.json"
    assert summary.exists()
    data = json.loads(summary.read_text())
    assert data.get("TODO") == 1
