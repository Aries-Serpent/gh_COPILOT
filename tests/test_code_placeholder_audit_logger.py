import json
import os
import sqlite3

os.environ["GH_COPILOT_DISABLE_VALIDATION"] = "1"

from scripts.dashboard_placeholder_sync import sync
from scripts.code_placeholder_audit import main, rollback_last_entry


def test_placeholder_audit_logger(tmp_path):
    workspace = tmp_path / "ws"
    workspace.mkdir()
    target = workspace / "demo.py"
    target.write_text("def x():\n    pass  # TODO\n")

    prod_db = tmp_path / "production.db"
    with sqlite3.connect(prod_db) as conn:
        conn.execute("CREATE TABLE template_placeholders (id INTEGER PRIMARY KEY, placeholder_name TEXT)")
        conn.execute("INSERT INTO template_placeholders (placeholder_name) VALUES ('legacy template logic')")

    analytics = tmp_path / "analytics.db"
    dash_dir = tmp_path / "dashboard" / "compliance"

    assert main(
        workspace_path=str(workspace),
        analytics_db=str(analytics),
        production_db=str(prod_db),
        dashboard_dir=str(dash_dir),
    )

    with sqlite3.connect(analytics) as conn:
        rows = conn.execute("SELECT placeholder_type FROM todo_fixme_tracking").fetchall()
        code_rows = conn.execute("SELECT placeholder_type FROM code_audit_log").fetchall()
    assert rows
    assert code_rows
    summary_file = dash_dir.joinpath("placeholder_summary.json")
    assert summary_file.exists()
    data = json.loads(summary_file.read_text())
    assert data["progress_status"] == "issues_pending"


def test_dashboard_placeholder_sync(tmp_path):
    dash = tmp_path / "dashboard" / "compliance"
    analytics = tmp_path / "analytics.db"
    analytics.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(analytics) as conn:
        conn.execute(
            (
                "CREATE TABLE todo_fixme_tracking (file_path TEXT, line_number INTEGER, placeholder_type TEXT, context TEXT, timestamp TEXT, resolved BOOLEAN DEFAULT 0, resolved_timestamp TEXT)"
            )
        )
        conn.execute(
            (
                "CREATE TABLE code_audit_log (id INTEGER PRIMARY KEY, file_path TEXT, line_number INTEGER, placeholder_type TEXT, context TEXT, timestamp TEXT)"
            )
        )
        conn.execute(
            (
                "INSERT INTO todo_fixme_tracking VALUES ('f', 1, 'TODO', 'ctx', 'ts', 0, NULL)"
            )
        )
        conn.execute(
            (
                "INSERT INTO code_audit_log (file_path, line_number, placeholder_type, context, timestamp) VALUES ('f', 1, 'TODO', 'ctx', 'ts')"
            )
        )
        conn.commit()

    sync(dash, analytics)
    data = json.loads(dash.joinpath("placeholder_summary.json").read_text())
    assert data["findings"] == 1
    assert data["progress_status"] == "issues_pending"


def test_rollback_last_entry(tmp_path):
    analytics = tmp_path / "analytics.db"
    analytics.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(analytics) as conn:
        conn.execute(
            (
                "CREATE TABLE todo_fixme_tracking (file_path TEXT, line_number INTEGER, placeholder_type TEXT, context TEXT, timestamp TEXT, resolved BOOLEAN DEFAULT 0, resolved_timestamp TEXT)"
            )
        )
        conn.execute(
            (
                "CREATE TABLE code_audit_log (id INTEGER PRIMARY KEY, "
                "file_path TEXT, line_number INTEGER, placeholder_type TEXT, "
                "context TEXT, timestamp TEXT)"
            )
        )
        conn.execute(
            (
                "INSERT INTO todo_fixme_tracking VALUES ('f', 1, 'TODO', 'ctx', 'ts', 0, NULL)"
            )
        )
        conn.execute(
            (
                "INSERT INTO code_audit_log (file_path, line_number, placeholder_type, "
                "context, timestamp) VALUES ('f', 1, 'TODO', 'ctx', 'ts')"
            )
        )
        conn.commit()

    assert rollback_last_entry(analytics)
    with sqlite3.connect(analytics) as conn:
        count = conn.execute("SELECT COUNT(*) FROM todo_fixme_tracking").fetchone()[0]
        count_log = conn.execute("SELECT COUNT(*) FROM code_audit_log").fetchone()[0]
    assert count == 0
    assert count_log == 0
