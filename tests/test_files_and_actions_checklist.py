import os
import sqlite3
from scripts.files_and_actions_checklist import main


def test_files_and_actions_checklist(tmp_path):
    workspace = tmp_path / "ws"
    workspace.mkdir()
    # create one expected file
    (workspace / "DATABASE_FIRST_COPILOT_TASK_SUGGESTIONS.md").write_text("x")

    prod_db = tmp_path / "prod.db"
    with sqlite3.connect(prod_db) as conn:
        conn.execute("CREATE TABLE checklist_patterns (pattern TEXT)")
        conn.execute("INSERT INTO checklist_patterns (pattern) VALUES ('extra.txt')")
        conn.commit()
    (workspace / "extra.txt").write_text("y")

    analytics = tmp_path / "analytics.db"
    report = tmp_path / "report.json"

    os.environ["GH_COPILOT_WORKSPACE"] = str(workspace)
    os.environ["GH_COPILOT_DISABLE_VALIDATION"] = "1"
    assert main(
        workspace=str(workspace),
        production_db=str(prod_db),
        analytics_db=str(analytics),
        report_path=str(report),
    )

    with sqlite3.connect(analytics) as conn:
        rows = conn.execute("SELECT file_path FROM file_audit").fetchall()
    assert len(rows) == 4
    assert report.exists()
