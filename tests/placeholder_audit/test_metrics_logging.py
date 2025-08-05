import json
import sqlite3
from types import SimpleNamespace

import secondary_copilot_validator

from scripts.code_placeholder_audit import main


def test_metrics_logged_and_dashboard_updated(tmp_path, monkeypatch):
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

    assert main(
        workspace_path=str(workspace),
        analytics_db=str(analytics),
        production_db=None,
        dashboard_dir=str(dash_dir / "compliance"),
    )

    metrics_file = dash_dir / "compliance" / "metrics.json"
    assert metrics_file.exists()
    metrics = json.loads(metrics_file.read_text())
    assert metrics["metrics"]["open_placeholders"] >= 1
    assert "progress" in metrics["metrics"]

    with sqlite3.connect(analytics) as conn:
        cur = conn.execute("SELECT open_placeholders, resolved_placeholders FROM placeholder_metrics")
        row = cur.fetchone()
        assert row[0] >= 1
        assert row[1] == 0
