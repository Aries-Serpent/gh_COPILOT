"""Integration tests for the DatabaseSynchronizationEngine."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from scripts.database_synchronization_engine import (
    DATABASE_SCHEMA_MAP,
    DatabaseSynchronizationEngine,
)


def _create_db(path: Path, rows: list[tuple[int, str, int]]) -> None:
    with sqlite3.connect(path) as conn:
        conn.execute("CREATE TABLE items (id INTEGER PRIMARY KEY, data TEXT, updated_at INTEGER)")
        conn.executemany(
            "INSERT INTO items (id, data, updated_at) VALUES (?, ?, ?)",
            rows,
        )


def _read_rows(path: Path) -> list[tuple[int, str, int]]:
    with sqlite3.connect(path) as conn:
        return conn.execute("SELECT id, data, updated_at FROM items ORDER BY id").fetchall()


def test_schema_map_contains_expected_keys() -> None:
    assert "production.db" in DATABASE_SCHEMA_MAP
    assert "analytics.db" in DATABASE_SCHEMA_MAP


def test_sync_updates_inserts_and_deletes(tmp_path: Path) -> None:
    source = tmp_path / "source.db"
    target = tmp_path / "target.db"
    log_file = Path("logs/synchronization.log")
    if log_file.exists():
        log_file.unlink()

    _create_db(source, [(1, "new", 2), (2, "insert", 1)])
    _create_db(target, [(1, "old", 1), (3, "remove", 1)])

    engine = DatabaseSynchronizationEngine(log_path=log_file)
    engine.sync(source, target)

    assert _read_rows(target) == [(1, "new", 2), (2, "insert", 1)]

    assert log_file.exists()
    log_content = log_file.read_text()
    assert "insert items:2" in log_content
    assert "delete items:3" in log_content
    assert "update items:1" in log_content


def test_log_hook_receives_events(tmp_path: Path) -> None:
    source = tmp_path / "src.db"
    target = tmp_path / "tgt.db"
    _create_db(source, [(1, "a", 1)])
    _create_db(target, [])

    events: list[tuple[str, str]] = []

    def hook(level: str, message: str) -> None:
        events.append((level, message))

    engine = DatabaseSynchronizationEngine(log_path=tmp_path / "log.log", log_hook=hook)
    engine.sync(source, target)

    assert any("insert items:1" in msg for _, msg in events)
