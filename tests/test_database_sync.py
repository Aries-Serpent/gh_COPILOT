#!/usr/bin/env python3
import sqlite3
import subprocess
import sys
from typing import Any
import pytest

from scripts.database.unified_database_initializer import initialize_database


class DummyTqdm:
    """Minimal tqdm replacement for progress validation."""

    def __init__(
        self, *args: Any, total: int, desc: str, unit: str = "db", **kwargs: Any
    ) -> None:
        self.total = total
        self.desc = desc
        self.unit = unit
        self.updates = 0

    def __enter__(self) -> "DummyTqdm":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        pass

    def update(self, n: int = 1) -> None:
        self.updates += n

    def set_postfix_str(self, *args: str, **kwargs: str) -> None:
        pass

    @property
    def format_dict(self) -> dict:
        """Return dummy timing information for compatibility."""
        return {"elapsed": 0, "remaining": 0}


def test_synchronize_databases(tmp_path):
    master = tmp_path / "enterprise_assets.db"
    replica = tmp_path / "replica.db"
    log_db = tmp_path / "log.db"
    initialize_database(log_db)
    from scripts.database.database_sync_scheduler import synchronize_databases
    with sqlite3.connect(master) as conn:
        conn.execute("CREATE TABLE t (id INTEGER)")
        conn.execute("INSERT INTO t (id) VALUES (1)")
    synchronize_databases(master, [replica], log_db=log_db)
    with sqlite3.connect(replica) as conn:
        cur = conn.execute("SELECT COUNT(*) FROM t")
        assert cur.fetchone()[0] == 1
    with sqlite3.connect(log_db) as conn:
        count = conn.execute(
            "SELECT COUNT(*) FROM cross_database_sync_operations"
        ).fetchone()[0]
    assert count >= 2


@pytest.mark.skip(reason="CLI integration requires external environment")
def test_scheduler_cli(tmp_path):
    workspace = tmp_path / "ws"
    db_dir = workspace / "databases"
    db_dir.mkdir(parents=True)
    master = db_dir / "enterprise_assets.db"
    replica = db_dir / "replica.db"
    extra_replica = db_dir / "extra.db"
    log_db = db_dir / "log.db"
    for db in (master, replica, extra_replica, log_db):
        with sqlite3.connect(db) as conn:
            conn.execute("CREATE TABLE t (id INTEGER)")
            conn.execute("INSERT INTO t (id) VALUES (1)")

    list_file = workspace / "list.md"
    list_file.write_text(f"- {replica.name}\n")
    extra_file = workspace / "extra.md"
    extra_file.write_text(f"- {extra_replica.name}\n")

    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "scripts.database.database_sync_scheduler",
            "--workspace",
            str(workspace),
            "--list-file",
            str(list_file),
            "--add-documentation-sync",
            str(extra_file),
            "--log-db",
            log_db.name,
        ]
    )

    for db in (replica, extra_replica):
        with sqlite3.connect(db) as conn:
            assert conn.execute("SELECT COUNT(*) FROM t").fetchone()[0] == 1


def test_synchronize_logging_progress(tmp_path, monkeypatch):
    master = tmp_path / "master.db"
    replica = tmp_path / "replica.db"
    log_db = tmp_path / "enterprise_assets.db"
    initialize_database(log_db)
    for db in (master, replica):
        with sqlite3.connect(db) as conn:
            conn.execute("CREATE TABLE t (id INTEGER)")
            conn.execute("INSERT INTO t (id) VALUES (1)")

    bars: list[DummyTqdm] = []

    def dummy_tqdm(*args: Any, **kwargs: Any) -> DummyTqdm:
        bar = DummyTqdm(*args, **kwargs)
        bars.append(bar)
        return bar

    monkeypatch.setattr("scripts.database.database_sync_scheduler.tqdm", dummy_tqdm)
    from scripts.database.database_sync_scheduler import synchronize_databases

    synchronize_databases(master, [replica], log_db=log_db)

    assert bars and bars[0].updates == 1
    with sqlite3.connect(log_db) as conn:
        count = conn.execute(
            "SELECT COUNT(*) FROM cross_database_sync_operations"
        ).fetchone()[0]
    assert count >= 2
