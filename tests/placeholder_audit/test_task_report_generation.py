import json
import sqlite3
from types import SimpleNamespace

from scripts.code_placeholder_audit import main
import secondary_copilot_validator


def test_task_report_written(tmp_path, monkeypatch):
    workspace = tmp_path / "ws"
    workspace.mkdir()
    (workspace / "a.py").write_text("# TODO\n")
    analytics = tmp_path / "analytics.db"
    dash_dir = tmp_path / "dashboard"

    monkeypatch.setenv("GH_COPILOT_DISABLE_VALIDATION", "1")
    monkeypatch.setattr(secondary_copilot_validator, "run_flake8", lambda *a, **k: True)
    monkeypatch.setattr(
        secondary_copilot_validator,
        "SecondaryCopilotValidator",
        lambda: SimpleNamespace(validate_corrections=lambda *a, **k: True),
    )
    monkeypatch.setattr(
        "scripts.code_placeholder_audit.ComplianceMetricsUpdater",
        lambda *a, **k: SimpleNamespace(update=lambda *a, **k: None, validate_update=lambda *a, **k: True),
    )

    report = tmp_path / "tasks.json"
    assert main(
        workspace_path=str(workspace),
        analytics_db=str(analytics),
        production_db=None,
        dashboard_dir=str(dash_dir),
        task_report=report,
    )

    assert report.exists()
    data = json.loads(report.read_text())
    assert data and data[0]["task"].startswith("Remove")
    with sqlite3.connect(analytics) as conn:
        status = conn.execute("SELECT status FROM todo_fixme_tracking").fetchone()[0]
    assert status == "open"
