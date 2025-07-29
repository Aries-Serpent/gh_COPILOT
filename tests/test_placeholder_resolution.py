import os
import sqlite3
import json

os.environ["GH_COPILOT_DISABLE_VALIDATION"] = "1"

from scripts.code_placeholder_audit import main


def test_placeholder_resolution(tmp_path):
    workspace = tmp_path / "ws"
    workspace.mkdir()
    target = workspace / "demo.py"
    target.write_text("def demo():\n    pass  # TODO\n")

    analytics = tmp_path / "analytics.db"

    assert main(
        workspace_path=str(workspace),
        analytics_db=str(analytics),
        production_db=None,
        dashboard_dir=str(tmp_path / "dashboard"),
    )

    target.write_text("def demo():\n    pass\n")
    assert main(
        workspace_path=str(workspace),
        analytics_db=str(analytics),
        production_db=None,
        dashboard_dir=str(tmp_path / "dashboard"),
    )

    dash_file = tmp_path / "dashboard" / "placeholder_summary.json"
    with sqlite3.connect(analytics) as conn:
        row = conn.execute(
            "SELECT resolved, resolved_timestamp FROM todo_fixme_tracking WHERE file_path=?",
            (str(target),),
        ).fetchone()
    assert row and row[0] == 1 and row[1] is not None
    data = json.loads(dash_file.read_text())
    assert data["resolved_count"] >= 1
