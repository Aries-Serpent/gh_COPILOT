import os
import sqlite3

os.environ["GH_COPILOT_DISABLE_VALIDATION"] = "1"

from scripts.code_placeholder_audit import main


def test_placeholder_logging(tmp_path):
    workspace = tmp_path / "ws"
    workspace.mkdir()
    target = workspace / "demo.py"
    target.write_text("def demo():\n    pass  # TODO\n")

    analytics = tmp_path / "analytics.db"
    dash_dir = tmp_path / "dashboard"
    os.environ["GH_COPILOT_WORKSPACE"] = str(workspace)

    assert main(
        workspace_path=str(workspace),
        analytics_db=str(analytics),
        production_db=None,
        dashboard_dir=str(dash_dir),
    )

    with sqlite3.connect(analytics) as conn:
        row = conn.execute("SELECT placeholder_type FROM todo_fixme_tracking").fetchone()
    assert row[0] == "TODO"
