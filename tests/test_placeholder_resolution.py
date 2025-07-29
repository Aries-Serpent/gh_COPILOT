import os
import sqlite3

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

    with sqlite3.connect(analytics) as conn:
        row = conn.execute(
            "SELECT resolved FROM todo_fixme_tracking WHERE file_path=?",
            (str(target),),
        ).fetchone()
    assert row and row[0] == 1
