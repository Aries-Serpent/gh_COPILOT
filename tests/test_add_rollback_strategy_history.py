import sqlite3
from pathlib import Path

from scripts.database.add_rollback_strategy_history import (
    add_table,
    ensure_rollback_strategy_history,
)


def test_add_rollback_strategy_history(tmp_path: Path) -> None:
    db = tmp_path / "analytics.db"
    add_table(db)
    ensure_rollback_strategy_history(db)
    with sqlite3.connect(db) as conn:
        conn.execute(
            "INSERT INTO rollback_strategy_history (target, strategy, outcome, timestamp)"
            " VALUES ('t', 's', 'success', 'ts')"
        )
        rows = conn.execute("SELECT target FROM rollback_strategy_history").fetchall()
    assert rows
