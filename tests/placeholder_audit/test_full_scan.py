import os
import sqlite3

from scripts.code_placeholder_audit import main
from tools import automation_setup as setup
from dashboard import integrated_dashboard as gui
import secondary_copilot_validator
from types import SimpleNamespace

os.environ["GH_COPILOT_DISABLE_VALIDATION"] = "1"


def test_full_scan_includes_all(tmp_path, monkeypatch):
    workspace = tmp_path / "ws"
    workspace.mkdir()
    (workspace / "builds").mkdir()
    (workspace / "builds" / "a.py").write_text("# TODO build\n")
    (workspace / "src").mkdir()
    (workspace / "src" / "b.py").write_text("# FIXME src\n")

    analytics = tmp_path / "analytics.db"
    dash_dir = tmp_path / "dashboard"

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
    assert main(
        workspace_path=str(workspace),
        analytics_db=str(analytics),
        production_db=None,
        dashboard_dir=str(dash_dir),
    )

    with sqlite3.connect(analytics) as conn:
        count = conn.execute("SELECT COUNT(*) FROM todo_fixme_tracking").fetchone()[0]
    assert count == 2


def test_test_mode_skips_db(tmp_path, monkeypatch):
    workspace = tmp_path / "ws"
    workspace.mkdir()
    (workspace / "file.py").write_text("# TODO\n")
    analytics = tmp_path / "analytics.db"
    dash_dir = tmp_path / "dashboard"
    monkeypatch.setenv("GH_COPILOT_TEST_MODE", "1")
    main(
        workspace_path=str(workspace),
        analytics_db=str(analytics),
        production_db=None,
        dashboard_dir=str(dash_dir),
    )
    with sqlite3.connect(analytics) as conn:
        count = conn.execute("SELECT COUNT(*) FROM todo_fixme_tracking").fetchone()[0]
    assert count == 0
    summary = dash_dir / "compliance" / "placeholder_summary.json"
    assert not summary.exists()


def test_run_placeholder_audit_exposes_results(tmp_path, monkeypatch):
    workspace = tmp_path / "ws"
    workspace.mkdir()
    (workspace / "file.py").write_text("# TODO\n")
    (workspace / "databases").mkdir()
    (workspace / "dashboard" / "compliance").mkdir(parents=True)

    monkeypatch.chdir(workspace)
    analytics = workspace / "databases" / "analytics.db"
    production = workspace / "databases" / "production.db"
    monkeypatch.setattr(gui, "ANALYTICS_DB", analytics)
    monkeypatch.setattr(gui, "METRICS_PATH", workspace / "metrics.json")
    monkeypatch.setattr(gui, "CORRECTIONS_DIR", workspace / "dashboard" / "compliance")
    monkeypatch.setattr(setup, "ANALYTICS_DB", analytics)
    monkeypatch.setattr(setup, "DB_PATH", production)

    setup.run_placeholder_audit()

    client = gui.app.test_client()
    data = client.get("/placeholder-audit").get_json()
    assert len(data["results"]) == 1
