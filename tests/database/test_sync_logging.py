import sqlite3
from pathlib import Path

import pytest

from src.database import sync_runner


def _setup_db(path: Path) -> None:
    conn = sqlite3.connect(path)
    conn.execute(
        "CREATE TABLE items(id INTEGER PRIMARY KEY, value TEXT, updated_at REAL)"
    )
    conn.commit()
    conn.close()


def _read_log() -> str:
    with sync_runner.LOG_FILE.open() as f:
        return f.read()


def test_run_sync_logs_success(tmp_path):
    if sync_runner.LOG_FILE.exists():
        sync_runner.LOG_FILE.write_text("")
    db_a = tmp_path / "a.db"
    db_b = tmp_path / "b.db"
    _setup_db(db_a)
    _setup_db(db_b)

    sync_runner.run_sync(db_a, db_b)

    log_content = _read_log()
    assert "Sync started" in log_content
    assert "Sync completed successfully" in log_content


def test_run_sync_logs_error(tmp_path, monkeypatch):
    if sync_runner.LOG_FILE.exists():
        sync_runner.LOG_FILE.write_text("")
    db_a = tmp_path / "a.db"
    db_b = tmp_path / "b.db"
    _setup_db(db_a)
    _setup_db(db_b)

    def boom(self, other):
        raise RuntimeError("boom")

    monkeypatch.setattr(sync_runner.Engine, "sync_with", boom)

    with pytest.raises(RuntimeError):
        sync_runner.run_sync(db_a, db_b)

    log_content = _read_log()
    assert "Sync started" in log_content
    assert "Sync failed" in log_content

