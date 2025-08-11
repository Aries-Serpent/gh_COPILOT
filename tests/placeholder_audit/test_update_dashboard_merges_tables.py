import json
import sqlite3

from scripts.code_placeholder_audit import log_placeholder_tasks, update_dashboard


def test_update_dashboard_merges_placeholder_tables(tmp_path) -> None:
    db = tmp_path / "analytics.db"
    tasks = [
        {"file": "a.py", "line": 1, "pattern": "TODO", "context": "todo", "suggestion": ""},
        {"file": "b.py", "line": 2, "pattern": "BUG", "context": "bug", "suggestion": ""},
        {"file": "c.py", "line": 3, "pattern": "FIXME", "context": "fix", "suggestion": ""},
    ]
    log_placeholder_tasks(tasks, db)
    with sqlite3.connect(db) as conn:
        conn.execute(
            "UPDATE placeholder_tasks SET status='resolved' WHERE pattern='FIXME'",
        )
        conn.commit()
    # record updated metrics reflecting resolved entry
    log_placeholder_tasks([], db)

    dash_dir = tmp_path / "dashboard"
    update_dashboard(dash_dir, db)

    summary = json.loads((dash_dir / "placeholder_summary.json").read_text())
    metrics = json.loads((dash_dir / "metrics.json").read_text())

    assert summary["findings"] == 2
    assert summary["resolved_count"] == 1
    assert summary["placeholder_counts"] == {"TODO": 1, "BUG": 1}
    assert metrics["metrics"]["open_placeholders"] == 2
    assert metrics["metrics"]["resolved_placeholders"] == 1

