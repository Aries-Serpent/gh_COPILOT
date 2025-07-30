import os
import sqlite3
from scripts.code_placeholder_audit import main

os.environ["GH_COPILOT_DISABLE_VALIDATION"] = "1"

def test_full_scan_includes_all(tmp_path):
    workspace = tmp_path / "ws"
    workspace.mkdir()
    (workspace / "builds").mkdir()
    (workspace / "builds" / "a.py").write_text("# TODO build\n")
    (workspace / "src").mkdir()
    (workspace / "src" / "b.py").write_text("# FIXME src\n")

    analytics = tmp_path / "analytics.db"
    dash_dir = tmp_path / "dashboard"

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
