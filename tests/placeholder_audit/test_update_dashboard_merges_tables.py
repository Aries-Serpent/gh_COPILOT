import json
import sqlite3

from scripts.code_placeholder_audit import update_dashboard


def test_update_dashboard_merges_placeholder_tables(tmp_path) -> None:
    db = tmp_path / "analytics.db"
    with sqlite3.connect(db) as conn:
        conn.execute(
            """
            CREATE TABLE todo_fixme_tracking (
                file_path TEXT,
                line_number INTEGER,
                placeholder_type TEXT,
                context TEXT,
                suggestion TEXT,
                status TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE placeholder_tasks (
                file_path TEXT,
                line_number INTEGER,
                pattern TEXT,
                context TEXT,
                suggestion TEXT,
                status TEXT
            )
            """
        )
        conn.execute(
            "INSERT INTO todo_fixme_tracking (file_path, line_number, placeholder_type, context, suggestion, status) VALUES ('a.py',1,'TODO','todo','', 'open')"
        )
        conn.execute(
            "INSERT INTO placeholder_tasks (file_path, line_number, pattern, context, suggestion, status) VALUES ('b.py',2,'BUG','bug','', 'open')"
        )
        conn.execute(
            "INSERT INTO placeholder_tasks (file_path, line_number, pattern, context, suggestion, status) VALUES ('c.py',3,'FIXME','fix','', 'resolved')"
        )
        conn.commit()

    dash_dir = tmp_path / "dashboard"
    update_dashboard(0, dash_dir, db)

    summary = json.loads((dash_dir / "placeholder_summary.json").read_text())
    metrics = json.loads((dash_dir / "metrics.json").read_text())

    assert summary["findings"] == 2
    assert summary["resolved_count"] == 1
    assert summary["placeholder_counts"] == {"TODO": 1, "BUG": 1}
    assert metrics["metrics"]["open_placeholders"] == 2
    assert metrics["metrics"]["resolved_placeholders"] == 1

