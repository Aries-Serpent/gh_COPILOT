"""Tests for :mod:`database_first_synchronization_engine`."""

from __future__ import annotations

import sqlite3
import threading
import time
from pathlib import Path

import pytest

from database_first_synchronization_engine import (
    SchemaMapper,
    SyncManager,
    SyncWatcher,
    ResolverPolicy,
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

    manager.sync(db_a, db_b, policy="last-write-wins")

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


def test_custom_merge_policy(tmp_path: Path) -> None:
    db_a = tmp_path / "a.db"
    db_b = tmp_path / "b.db"

    _create_db(db_a, [(1, "a", 1)])
    _create_db(db_b, [(1, "b", 2)])

    mapper = SchemaMapper()
    manager = SyncManager(mapper)

    calls: list[str] = []

    def merge(table: str, row_a: dict, row_b: dict) -> dict:
        calls.append(table)
        return {**row_a, "data": row_a["data"] + row_b["data"], "updated_at": row_b["updated_at"]}

    manager.sync(db_a, db_b, policy=ResolverPolicy(merge))

    assert calls == ["items"]
    assert _read_rows(db_a) == [(1, "ab", 2)]
    assert _read_rows(db_b) == [(1, "ab", 2)]


def test_watch_pairs_syncs_multiple_pairs(tmp_path: Path) -> None:
    db1_a = tmp_path / "a1.db"
    db1_b = tmp_path / "b1.db"
    db2_a = tmp_path / "a2.db"
    db2_b = tmp_path / "b2.db"
    analytics = tmp_path / "analytics.db"

    _create_db(db1_a, [(1, "a", 1)])
    _create_db(db1_b, [(1, "b", 2)])
    _create_db(db2_a, [(1, "x", 1)])
    _create_db(db2_b, [(1, "y", 2)])

    manager = SyncManager(SchemaMapper(), analytics_db=analytics)
    watcher = SyncWatcher(manager)

    stop = threading.Event()
    t = threading.Thread(
        target=watcher.watch_pairs,
        args=([(db1_a, db1_b), (db2_a, db2_b)],),
        kwargs={"interval": 0.1, "stop_event": stop, "policy": "last-write-wins"},
    )
    t.start()
    try:
        with sqlite3.connect(db1_a) as conn:
            conn.execute("UPDATE items SET data='new1', updated_at=3 WHERE id=1")
            conn.commit()
        with sqlite3.connect(db2_b) as conn:
            conn.execute("UPDATE items SET data='new2', updated_at=3 WHERE id=1")
            conn.commit()
        time.sleep(0.5)
    finally:
        stop.set()
        t.join()

    assert _read_rows(db1_a) == [(1, "new1", 3)]
    assert _read_rows(db1_b) == [(1, "new1", 3)]
    assert _read_rows(db2_a) == [(1, "new2", 3)]
    assert _read_rows(db2_b) == [(1, "new2", 3)]


def test_tables_without_id_are_skipped(tmp_path: Path) -> None:
    db_a = tmp_path / "a.db"
    db_b = tmp_path / "b.db"

    _create_db(db_a, [(1, "a", 1)])
    _create_db(db_b, [(1, "b", 2)])
    with sqlite3.connect(db_a) as conn:
        conn.execute("CREATE TABLE noid (data TEXT)")
        conn.execute("INSERT INTO noid (data) VALUES ('A')")
    with sqlite3.connect(db_b) as conn:
        conn.execute("CREATE TABLE noid (data TEXT)")
        conn.execute("INSERT INTO noid (data) VALUES ('B')")

    manager = SyncManager(SchemaMapper())
    manager.sync(db_a, db_b, policy="last-write-wins")

    # items table synchronized
    assert _read_rows(db_a) == [(1, "b", 2)]
    assert _read_rows(db_b) == [(1, "b", 2)]

    # noid tables remain untouched
    with sqlite3.connect(db_a) as conn:
        a_noid = conn.execute("SELECT data FROM noid").fetchall()
    with sqlite3.connect(db_b) as conn:
        b_noid = conn.execute("SELECT data FROM noid").fetchall()
    assert a_noid == [("A",)]
    assert b_noid == [("B",)]


def test_malicious_table_name_rejected(tmp_path: Path) -> None:
    db_a = tmp_path / "a.db"
    db_b = tmp_path / "b.db"

    with sqlite3.connect(db_a) as conn:
        conn.execute('CREATE TABLE "bad-name" (id INTEGER PRIMARY KEY)')
    with sqlite3.connect(db_b) as conn:
        conn.execute('CREATE TABLE "bad-name" (id INTEGER PRIMARY KEY)')

    manager = SyncManager(SchemaMapper())
    with pytest.raises(ValueError):
        manager.sync(db_a, db_b)
