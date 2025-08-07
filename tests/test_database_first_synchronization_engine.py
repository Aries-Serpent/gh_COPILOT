"""Tests for :mod:`database_first_synchronization_engine`."""

from __future__ import annotations

import sqlite3
import threading
import time
from pathlib import Path

from database_first_synchronization_engine import (
    SchemaMapper,
    SyncManager,
    list_events,
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


def test_bidirectional_sync_and_logging(tmp_path: Path) -> None:
    db_a = tmp_path / "a.db"
    db_b = tmp_path / "b.db"
    analytics = tmp_path / "analytics.db"

    _create_db(db_a, [(1, "a", 1), (2, "from_a", 2)])
    _create_db(db_b, [(1, "b", 3), (3, "from_b", 3)])

    mapper = SchemaMapper()
    manager = SyncManager(mapper, analytics_db=analytics)

    calls: list[tuple[str, int]] = []

    def resolver(table: str, row_a: dict, row_b: dict) -> dict:
        calls.append((table, row_a["id"]))
        return row_a if row_a["updated_at"] >= row_b["updated_at"] else row_b

    manager.sync(db_a, db_b, resolver=resolver)

    assert _read_rows(db_a) == [
        (1, "b", 3),
        (2, "from_a", 2),
        (3, "from_b", 3),
    ]
    assert _read_rows(db_b) == [
        (1, "b", 3),
        (2, "from_a", 2),
        (3, "from_b", 3),
    ]
    assert calls  # conflict resolver invoked

    with sqlite3.connect(analytics) as conn:
        rows = conn.execute(
            "SELECT source_db, target_db, action, status FROM synchronization_events"
        ).fetchall()
        assert rows[0][2] == "sync" and rows[0][3] == "success"
        conflicts = conn.execute(
            "SELECT table_name, row_id, decision FROM synchronization_conflicts"
        ).fetchall()
        assert conflicts

    events = list_events(analytics, limit=1)
    assert events and events[0]["action"] == "sync" and events[0]["status"] == "success"


def test_watch_triggers_sync_on_change(tmp_path: Path) -> None:
    db_a = tmp_path / "a.db"
    db_b = tmp_path / "b.db"
    analytics = tmp_path / "analytics.db"

    _create_db(db_a, [(1, "a", 1)])
    _create_db(db_b, [(1, "b", 2)])

    mapper = SchemaMapper()
    manager = SyncManager(mapper, analytics_db=analytics)

    stop = threading.Event()
    t = threading.Thread(target=manager.watch, args=(db_a, db_b), kwargs={"interval": 0.1, "stop_event": stop})
    t.start()
    try:
        with sqlite3.connect(db_a) as conn:
            conn.execute("UPDATE items SET data='new', updated_at=3 WHERE id=1")
            conn.commit()
        time.sleep(0.3)
    finally:
        stop.set()
        t.join()

    assert _read_rows(db_a) == [(1, "new", 3)]
    assert _read_rows(db_b) == [(1, "new", 3)]
    events = list_events(analytics, limit=1)
    assert events and events[0]["status"] == "success"
