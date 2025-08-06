import os
import sqlite3
from types import SimpleNamespace

import secondary_copilot_validator
from scripts.code_placeholder_audit import main

os.environ["GH_COPILOT_DISABLE_VALIDATION"] = "1"


def test_auto_resolve_updates_db_and_file(tmp_path, monkeypatch):
    workspace = tmp_path / "ws"
    workspace.mkdir()
    target = workspace / "sample.py"
    target.write_text("x = 1  # TODO remove\n")
    analytics = tmp_path / "analytics.db"
    dash_dir = tmp_path / "dashboard"
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))

    monkeypatch.setattr(
        secondary_copilot_validator,
        "run_flake8",
        lambda *a, **k: True,
    )
    monkeypatch.setattr(
        secondary_copilot_validator,
        "SecondaryCopilotValidator",
        lambda: SimpleNamespace(validate_corrections=lambda *a, **k: True),
    )
    monkeypatch.setattr(
        "scripts.code_placeholder_audit.ComplianceMetricsUpdater",
        lambda *a, **k: SimpleNamespace(update=lambda *a, **k: None, validate_update=lambda *a, **k: None),
    )
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

    assert main(
        workspace_path=str(workspace),
        analytics_db=str(analytics),
        production_db=None,
        dashboard_dir=str(dash_dir),
        auto_resolve=True,
    )

    assert "TODO" not in target.read_text()

    with sqlite3.connect(analytics) as conn:
        row = conn.execute(
            "SELECT resolved, status FROM todo_fixme_tracking"
        ).fetchone()
        rationale = conn.execute(
            "SELECT rationale FROM corrections"
        ).fetchone()[0]
    assert row == (1, "resolved")
    assert "Remove TODO" in rationale
