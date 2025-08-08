"""Logging tests for the SQLite SyncEngine."""

import logging
import sqlite3
import pytest

from db.engine.sync import SyncEngine


def _engine() -> tuple[SyncEngine, sqlite3.Connection, sqlite3.Connection]:
    src = sqlite3.connect(":memory:", check_same_thread=False)
    dst = sqlite3.connect(":memory:", check_same_thread=False)
    src.execute("CREATE TABLE items (id INTEGER PRIMARY KEY, value TEXT)")
    dst.execute("CREATE TABLE items (id INTEGER PRIMARY KEY, value TEXT)")
    engine = SyncEngine(src, dst, "items")
    engine.stop()  # stop background thread for deterministic logging
    return engine, src, dst


def test_process_logs_start_and_end(caplog):
    engine, src, dst = _engine()
    with caplog.at_level(logging.INFO, logger="sync"):
        engine._process(src, dst)
    assert caplog.messages == ["start", "end"]


def test_process_logs_error(caplog):
    engine, src, dst = _engine()
    src.execute("INSERT INTO items (id, value) VALUES (1, 'a')")
    src.commit()

    def boom(*args, **kwargs):
        raise RuntimeError("boom")

    engine._apply_change = boom  # type: ignore[assignment]

    with caplog.at_level(logging.INFO, logger="sync"):
        with pytest.raises(RuntimeError):
            engine._process(src, dst)
    assert caplog.messages == ["start", "error"]
