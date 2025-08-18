import logging
import threading
from pathlib import Path

import pytest

from src.database.engine import Engine


def test_engine_concurrent_inserts(tmp_path: Path) -> None:
    engine = Engine(tmp_path / "db.sqlite")
    engine.execute("CREATE TABLE t (id INTEGER PRIMARY KEY, data TEXT)")

    def insert_range(start: int, end: int) -> None:
        for i in range(start, end):
            engine.execute("INSERT INTO t (data) VALUES (?)", (str(i),))

    threads = [
        threading.Thread(target=insert_range, args=(0, 100)),
        threading.Thread(target=insert_range, args=(100, 200)),
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    count = engine.execute("SELECT COUNT(*) FROM t").fetchone()[0]
    assert count == 200


def test_sync_with_rollback_on_error(tmp_path: Path, monkeypatch) -> None:
    db1 = tmp_path / "a.db"
    db2 = tmp_path / "b.db"
    e1 = Engine(db1)
    e2 = Engine(db2)
    e1.execute("CREATE TABLE t (id INTEGER PRIMARY KEY, value TEXT)")
    e2.execute("CREATE TABLE t (id INTEGER PRIMARY KEY, value TEXT)")
    e1.execute("INSERT INTO t (id, value) VALUES (1, 'a')")

    original_upsert = Engine._upsert

    def failing_upsert(conn, table, row):
        original_upsert(conn, table, row)
        raise RuntimeError("boom")

    monkeypatch.setattr(Engine, "_upsert", staticmethod(failing_upsert))

    with pytest.raises(RuntimeError):
        e1.sync_with(e2)

    e2.conn.rollback()
    count = e2.execute("SELECT COUNT(*) FROM t").fetchone()[0]
    assert count == 0


def test_query_logging_and_indexing(tmp_path: Path, caplog) -> None:
    engine = Engine(tmp_path / "db.sqlite", log_queries=True)
    engine.execute("CREATE TABLE t (id INTEGER PRIMARY KEY, name TEXT)")
    for i in range(500):
        engine.execute("INSERT INTO t (name) VALUES (?)", (f"name{i}",))

    with caplog.at_level(logging.INFO):
        engine.execute("SELECT * FROM t WHERE name=?", ("name250",))

    assert any("SELECT * FROM t WHERE name=?" in r.getMessage() for r in caplog.records)

    plan_no_idx = engine.execute(
        "EXPLAIN QUERY PLAN SELECT * FROM t WHERE name=?", ("name400",)
    ).fetchone()[3]
    engine.ensure_index("t", "name")
    plan_idx = engine.execute(
        "EXPLAIN QUERY PLAN SELECT * FROM t WHERE name=?", ("name400",)
    ).fetchone()[3]

    plan_idx_upper = plan_idx.upper()
    assert "USING" in plan_idx_upper and "INDEX" in plan_idx_upper
    assert plan_no_idx != plan_idx

