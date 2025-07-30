import os
import sqlite3

os.environ["GH_COPILOT_DISABLE_VALIDATION"] = "1"

from scripts.code_placeholder_audit import main


def test_exclude_directories(tmp_path):
    workspace = tmp_path / "ws"
    workspace.mkdir()
    (workspace / "builds").mkdir()
    (workspace / "builds" / "gen.py").write_text("# TODO generated\n")
    (workspace / "src").mkdir()
    (workspace / "src" / "real.py").write_text("# TODO real\n")

    analytics = tmp_path / "analytics.db"
    dash_dir = tmp_path / "dashboard"

    assert main(
        workspace_path=str(workspace),
        analytics_db=str(analytics),
        production_db=None,
        dashboard_dir=str(dash_dir),
    )

    with sqlite3.connect(analytics) as conn:
        rows = conn.execute("SELECT file_path FROM todo_fixme_tracking").fetchall()
    assert len(rows) == 1
    assert "src/real.py" in rows[0][0]

    analytics.unlink()
    assert main(
        workspace_path=str(workspace),
        analytics_db=str(analytics),
        production_db=None,
        dashboard_dir=str(dash_dir),
        exclude_dirs=[],
    )
    with sqlite3.connect(analytics) as conn:
        rows = conn.execute("SELECT COUNT(*) FROM todo_fixme_tracking").fetchone()
    assert rows[0] == 2
