import sqlite3
from pathlib import Path

from db_tools.database_synchronization_engine import (
    DATABASE_SCHEMA_MAP,
    DatabaseSynchronizationEngine,
)


def _create_db(path: Path, rows: list[tuple[int, str, int]]) -> None:
    with sqlite3.connect(path) as conn:
        conn.execute(
            "CREATE TABLE items (id INTEGER PRIMARY KEY, data TEXT, updated_at INTEGER)"
        )
        conn.executemany(
            "INSERT INTO items (id, data, updated_at) VALUES (?, ?, ?)",
            rows,
        )


def _read_rows(path: Path) -> list[tuple[int, str, int]]:
    with sqlite3.connect(path) as conn:
        return conn.execute(
            "SELECT id, data, updated_at FROM items ORDER BY id"
        ).fetchall()


def test_schema_map_contains_expected_keys() -> None:
    assert "production.db" in DATABASE_SCHEMA_MAP
    assert "analytics.db" in DATABASE_SCHEMA_MAP


def test_sync_audit_log_captures_actions(tmp_path: Path) -> None:
    source = tmp_path / "source.db"
    target = tmp_path / "target.db"
    audit = tmp_path / "analytics.db"
    log_file = tmp_path / "sync.log"

    _create_db(source, [(1, "new", 2), (2, "insert", 1), (4, "stale", 1)])
    _create_db(target, [(1, "old", 1), (3, "remove", 1), (4, "fresh", 5)])

    engine = DatabaseSynchronizationEngine(log_path=log_file, audit_db_path=audit)
    engine.sync(source, target)

    assert _read_rows(target) == [
        (1, "new", 2),
        (2, "insert", 1),
        (4, "fresh", 5),
    ]

    log_content = log_file.read_text()
    assert "insert items:2" in log_content
    assert "update items:1" in log_content
    assert "delete items:3" in log_content
    assert "conflict_skip items:4" in log_content

    with sqlite3.connect(audit) as conn:
        actions = [
            row[0] for row in conn.execute(
                "SELECT action FROM sync_audit_log ORDER BY id"
            ).fetchall()
        ]
    assert set(actions) == {
        "insert items:2",
        "update items:1",
        "delete items:3",
        "conflict_skip items:4",
    }
