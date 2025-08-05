import json
import sqlite3
from types import SimpleNamespace

from scripts.code_placeholder_audit import main as audit_main
from scripts.placeholder_enforcer import main as enforce_main
import secondary_copilot_validator


def test_placeholder_enforcer_updates_tracking(tmp_path, monkeypatch):
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
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
    audit_main(
        workspace_path=str(workspace),
        analytics_db=str(analytics),
        production_db=None,
        dashboard_dir=str(dash_dir),
        task_report=report,
    )
    assert json.loads(report.read_text())

    ticket_dir = tmp_path / "tickets"
    monkeypatch.setattr(
        "scripts.placeholder_enforcer.ComplianceMetricsUpdater",
        lambda *a, **k: SimpleNamespace(update=lambda *a, **k: None, validate_update=lambda *a, **k: True),
    )
    created = enforce_main(
        report=str(report),
        analytics_db=str(analytics),
        ticket_dir=str(ticket_dir),
        dashboard_dir=str(dash_dir),
    )

    assert created == 1
    assert ticket_dir.exists()
    assert len(list(ticket_dir.iterdir())) == 1
    with sqlite3.connect(analytics) as conn:
        status = conn.execute("SELECT status FROM todo_fixme_tracking").fetchone()[0]
    assert status == "ticketed"
