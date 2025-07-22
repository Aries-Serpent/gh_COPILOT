import json
import sqlite3

from scripts.placeholder_audit_logger import main
from scripts.dashboard_placeholder_sync import sync


def test_placeholder_audit_logger(tmp_path):
    workspace = tmp_path / "ws"
    workspace.mkdir()
    target = workspace / "demo.py"
    target.write_text("def x():\n    pass  # TODO\n")

    prod_db = tmp_path / "production.db"
    with sqlite3.connect(prod_db) as conn:
        conn.execute(
            "CREATE TABLE template_placeholders (id INTEGER PRIMARY KEY, placeholder_name TEXT)"
        )
        conn.execute(
            "INSERT INTO template_placeholders (placeholder_name) VALUES ('legacy template logic')"
        )
        conn.commit()

    analytics = tmp_path / "analytics.db"
    dash_dir = tmp_path / "dashboard" / "compliance"

    assert main(
        workspace_path=str(workspace),
        analytics_db=str(analytics),
        production_db=str(prod_db),
        dashboard_dir=str(dash_dir),
    )

    with sqlite3.connect(analytics) as conn:
        rows = conn.execute("SELECT pattern FROM placeholder_audit").fetchall()
    assert rows
    assert dash_dir.joinpath("placeholder_summary.json").exists()


def test_dashboard_placeholder_sync(tmp_path):
    dash = tmp_path / "dashboard" / "compliance"
    analytics = tmp_path / "analytics.db"
    analytics.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(analytics) as conn:
        conn.execute(
            "CREATE TABLE placeholder_audit (id INTEGER PRIMARY KEY, file_path TEXT, pattern TEXT, line INTEGER, severity TEXT, ts TEXT)"
        )
        conn.execute(
            "INSERT INTO placeholder_audit (file_path, pattern, line, severity, ts) VALUES ('f', 'TODO', 1, 'low', 'ts')"
        )
        conn.execute(
            "INSERT INTO placeholder_audit (file_path, pattern, line, severity, ts) VALUES ('f', 'FIXME', 2, 'medium', 'ts')"
        )
        conn.commit()

    sync(dash, analytics)
    data = json.loads(dash.joinpath("placeholder_summary.json").read_text())
    assert data["findings"] == 2

