import sqlite3
import importlib


def test_dashboard_reads_tracking_table(tmp_path, monkeypatch) -> None:
    db = tmp_path / "analytics.db"
    dash_dir = tmp_path / "dashboard"
    dash_dir.mkdir()
    with sqlite3.connect(db) as conn:
        conn.execute(
            """
            CREATE TABLE todo_fixme_tracking (
                file_path TEXT,
                line_number INTEGER,
                placeholder_type TEXT,
                context TEXT,
                suggestion TEXT,
                status TEXT
            )
            """
        )
        conn.execute(
            "INSERT INTO todo_fixme_tracking (file_path, line_number, placeholder_type, context, suggestion, status) VALUES ('a.py',1,'TODO','TODO','', 'open')"
        )
        conn.execute(
            "INSERT INTO todo_fixme_tracking (file_path, line_number, placeholder_type, context, suggestion, status) VALUES ('b.py',2,'FIXME','FIXME','', 'resolved')"
        )
        conn.commit()

    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    monkeypatch.setenv("GH_COPILOT_DISABLE_VALIDATION", "1")
    monkeypatch.setattr(
        "scripts.database.add_violation_logs.ensure_violation_logs", lambda *a, **k: None
    )
    monkeypatch.setattr(
        "enterprise_modules.compliance.ensure_violation_logs", lambda *a, **k: None
    )
    monkeypatch.setattr(
        "scripts.correction_logger_and_rollback.ensure_violation_logs", lambda *a, **k: None
    )
    monkeypatch.setattr(
        "scripts.database.add_rollback_logs.ensure_rollback_logs", lambda *a, **k: None
    )
    monkeypatch.setattr(
        "enterprise_modules.compliance.ensure_rollback_logs", lambda *a, **k: None
    )
    monkeypatch.setattr(
        "scripts.correction_logger_and_rollback.ensure_rollback_logs", lambda *a, **k: None
    )
    mod = importlib.reload(importlib.import_module("dashboard.compliance_metrics_updater"))
    monkeypatch.setattr(mod, "ANALYTICS_DB", db)
    updater = mod.ComplianceMetricsUpdater(dash_dir, test_mode=True)
    metrics = updater._fetch_compliance_metrics(test_mode=True)
    assert metrics["open_placeholders"] == 1
    assert metrics["resolved_placeholders"] == 1
    assert metrics["placeholder_breakdown"] == {"TODO": 1}

