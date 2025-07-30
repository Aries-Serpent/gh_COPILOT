import os
import sqlite3

os.environ["GH_COPILOT_DISABLE_VALIDATION"] = "1"
os.environ["GH_COPILOT_USER"] = "tester"

from scripts.code_placeholder_audit import main, rollback_audit_entry


def test_history_fields(tmp_path):
    workspace = tmp_path / "ws"
    workspace.mkdir()
    target = workspace / "demo.py"
    target.write_text("# TODO demo\n")

    analytics = tmp_path / "analytics.db"

    assert main(
        workspace_path=str(workspace),
        analytics_db=str(analytics),
        production_db=None,
        dashboard_dir=str(tmp_path / "dash"),
    )

    with sqlite3.connect(analytics) as conn:
        row = conn.execute("SELECT author, resolved_by, resolved_timestamp FROM todo_fixme_tracking").fetchone()
    assert row == ("tester", None, None)

    target.write_text("pass\n")
    assert main(
        workspace_path=str(workspace),
        analytics_db=str(analytics),
        production_db=None,
        dashboard_dir=str(tmp_path / "dash"),
        update_resolutions=True,
    )

    with sqlite3.connect(analytics) as conn:
        row = conn.execute("SELECT resolved, resolved_by, resolved_timestamp FROM todo_fixme_tracking").fetchone()
    assert row[0] == 1
    assert row[1] == "tester"
    assert row[2] is not None


def test_rollback_audit_entry(tmp_path):
    db = tmp_path / "analytics.db"
    with sqlite3.connect(db) as conn:
        conn.execute(
            """CREATE TABLE todo_fixme_tracking (
                file_path TEXT,
                line_number INTEGER,
                placeholder_type TEXT,
                context TEXT,
                timestamp TEXT,
                author TEXT,
                resolved BOOLEAN DEFAULT 0,
                resolved_timestamp TEXT,
                resolved_by TEXT,
                status TEXT,
                removal_id INTEGER
            )"""
        )
        conn.execute(
            """CREATE TABLE code_audit_log (
                id INTEGER PRIMARY KEY,
                file_path TEXT,
                line_number INTEGER,
                placeholder_type TEXT,
                context TEXT,
                timestamp TEXT
            )"""
        )
        conn.execute(
            "INSERT INTO todo_fixme_tracking VALUES ('f',1,'TODO','ctx','ts','tester',0,NULL,NULL,'open',NULL)"
        )
        conn.execute(
            "INSERT INTO code_audit_log (file_path, line_number, placeholder_type, context, timestamp) VALUES ('f',1,'TODO','ctx','ts')"
        )
        conn.commit()

    assert rollback_audit_entry(db, 1)
    with sqlite3.connect(db) as conn:
        count = conn.execute("SELECT COUNT(*) FROM todo_fixme_tracking").fetchone()[0]
        code_count = conn.execute("SELECT COUNT(*) FROM code_audit_log").fetchone()[0]
    assert count == 0
    assert code_count == 0
