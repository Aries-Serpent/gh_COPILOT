import sqlite3
from pathlib import Path

from scripts.codex_log_db import init_db, log_action


def test_log_action_creates_entry(tmp_path: Path) -> None:
    db_path = tmp_path / "codex_logs.db"
    init_db(db_path)
    log_action("test", "example", db_path=db_path)
    with sqlite3.connect(db_path) as conn:
        cur = conn.execute("SELECT action, statement FROM codex_logs")
        rows = cur.fetchall()
    assert rows == [("test", "example")]
