from pathlib import Path
import sqlite3

from scripts.code_placeholder_audit import log_placeholder_tasks


def test_placeholder_task_persistence(tmp_path: Path) -> None:
    db = tmp_path / "analytics.db"
    tasks = [
        {
            "task": "Remove TODO in foo.py:10 - TODO",
            "file": "foo.py",
            "line": "10",
            "pattern": "TODO",
            "context": "TODO",
            "suggestion": "fix",
        }
    ]
    inserted = log_placeholder_tasks(tasks, db, simulate=False)
    assert inserted == 1
    with sqlite3.connect(db) as conn:
        row = conn.execute(
            "SELECT file_path, line_number, placeholder_type, context, suggestion, status FROM todo_fixme_tracking"
        ).fetchone()
    assert row == ("foo.py", 10, "TODO", "TODO", "fix", "open")

