from pathlib import Path

import sqlite3

from scripts.database.add_violation_logs import add_table as add_violation_table, ensure_violation_logs
from scripts.database.add_rollback_logs import add_table as add_rollback_table, ensure_rollback_logs


def test_add_violation_logs(tmp_path: Path) -> None:
    db = tmp_path / "analytics.db"
    add_violation_table(db)
    ensure_violation_logs(db)
    with sqlite3.connect(db) as conn:
        conn.execute("INSERT INTO violation_logs (timestamp, details) VALUES ('ts', 'd')")
        rows = conn.execute("SELECT details FROM violation_logs").fetchall()
    assert rows


def test_add_rollback_logs(tmp_path: Path) -> None:
    db = tmp_path / "analytics.db"
    add_rollback_table(db)
    ensure_rollback_logs(db)
    with sqlite3.connect(db) as conn:
        conn.execute("INSERT INTO rollback_logs (target, backup, timestamp) VALUES ('t', 'b', 'ts')")
        rows = conn.execute("SELECT target FROM rollback_logs").fetchall()
    assert rows
