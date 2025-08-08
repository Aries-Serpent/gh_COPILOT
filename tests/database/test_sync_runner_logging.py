from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from src.database.sync_runner import run_sync


def _empty_db(path: Path) -> None:
    with sqlite3.connect(path) as conn:
        conn.execute("CREATE TABLE t (id INTEGER)")


def test_run_sync_logging(tmp_path: Path) -> None:
    a = tmp_path / "a.db"
    b = tmp_path / "b.db"
    _empty_db(a)
    _empty_db(b)
    events: list[tuple[str, dict]] = []
    run_sync(a, b, log_hook=lambda e, ctx: events.append((e, ctx)))
    assert events[0][0] == "sync.start"
    assert events[-1][0] == "sync.end"


def test_run_sync_logging_error(tmp_path: Path, monkeypatch) -> None:
    a = tmp_path / "a.db"
    b = tmp_path / "b.db"
    _empty_db(a)
    _empty_db(b)

    def boom(*_args, **_kwargs):  # pragma: no cover - raised for logging
        raise RuntimeError("fail")

    monkeypatch.setattr("src.database.sync_runner.Engine.sync_with", boom)
    events: list[tuple[str, dict]] = []
    with pytest.raises(RuntimeError):
        run_sync(a, b, log_hook=lambda e, ctx: events.append((e, ctx)))
    assert any(e == "sync.error" for e, _ in events)

