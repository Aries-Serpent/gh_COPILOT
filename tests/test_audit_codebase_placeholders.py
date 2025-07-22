import os
import sqlite3

from scripts.audit_codebase_placeholders import main


def test_audit_places(tmp_path):
    workspace = tmp_path / "ws"
    workspace.mkdir()
    target = workspace / "demo.py"
    target.write_text("def x():\n    pass  # TODO\n    # Implementation placeholder\n")

    prod_db = tmp_path / "production.db"
    with sqlite3.connect(prod_db) as conn:
        conn.execute(
            "CREATE TABLE template_placeholders (id INTEGER PRIMARY KEY, placeholder_name TEXT)"
        )
        conn.execute("INSERT INTO template_placeholders (placeholder_name) VALUES ('legacy template logic')")
        conn.commit()

    analytics = tmp_path / "analytics.db"
    dash_dir = tmp_path / "dashboard" / "compliance"

    os.environ["GH_COPILOT_WORKSPACE"] = str(workspace)
    assert main(
        workspace_path=str(workspace),
        analytics_db=str(analytics),
        production_db=str(prod_db),
        dashboard_dir=str(dash_dir),
    )

    with sqlite3.connect(analytics) as conn:
        rows = conn.execute("SELECT item_type FROM todo_fixme_tracking").fetchall()
        rows2 = conn.execute("SELECT placeholder_type FROM code_audit_log").fetchall()
    assert len(rows) >= 2
    assert len(rows2) >= 2
    assert dash_dir.joinpath("placeholder_summary.json").exists()
