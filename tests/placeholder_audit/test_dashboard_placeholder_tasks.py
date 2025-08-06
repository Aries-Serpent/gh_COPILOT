import sqlite3
import importlib


def test_dashboard_reads_placeholder_tasks(tmp_path, monkeypatch) -> None:
    db = tmp_path / "analytics.db"
    dash_dir = tmp_path / "dashboard"
    dash_dir.mkdir()
    with sqlite3.connect(db) as conn:
        conn.execute(
            """
            CREATE TABLE placeholder_tasks (
                id INTEGER PRIMARY KEY,
                file TEXT,
                line INTEGER,
                pattern TEXT,
                context TEXT,
                suggestion TEXT,
                status TEXT
            )
            """
        )
        conn.execute(
            "INSERT INTO placeholder_tasks (file, line, pattern, context, suggestion, status) VALUES ('a.py',1,'TODO','TODO','', 'open')"
        )
        conn.execute(
            "INSERT INTO placeholder_tasks (file, line, pattern, context, suggestion, status) VALUES ('b.py',2,'FIXME','FIXME','', 'resolved')"
        )
        conn.commit()

    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    mod = importlib.reload(importlib.import_module("dashboard.compliance_metrics_updater"))
    monkeypatch.setattr(mod, "ANALYTICS_DB", db)
    updater = mod.ComplianceMetricsUpdater(dash_dir, test_mode=True)
    metrics = updater._fetch_compliance_metrics(test_mode=True)
    assert metrics["open_placeholders"] == 1
    assert metrics["resolved_placeholders"] == 1
    assert metrics["placeholder_breakdown"] == {"TODO": 1}

