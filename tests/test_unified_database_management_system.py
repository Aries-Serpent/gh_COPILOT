import sqlite3
from pathlib import Path
from typing import Any, List

import pytest

from scripts.database.unified_database_management_system import (
    _backup_database,
    synchronize_databases,
)
from scripts.database.unified_database_initializer import initialize_database


class DummyTqdm:
    """Minimal tqdm replacement for testing."""

    def __init__(self, *args: Any, total: int, desc: str, unit: str = "", **kwargs: Any) -> None:
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


def test_backup_database_logs(tmp_path: Path) -> None:
    master = tmp_path / "master.db"
    replica = tmp_path / "replica.db"
    log_db = tmp_path / "enterprise_assets.db"
    initialize_database(log_db)
    with sqlite3.connect(master) as conn:
        conn.execute("CREATE TABLE t (id INTEGER)")
        conn.execute("INSERT INTO t (id) VALUES (1)")
    _backup_database(master, replica, log_db=log_db)
    with sqlite3.connect(replica) as conn:
        assert conn.execute("SELECT COUNT(*) FROM t").fetchone()[0] == 1
    with sqlite3.connect(log_db) as conn:
        count = conn.execute(
            "SELECT COUNT(*) FROM cross_database_sync_operations"
        ).fetchone()[0]
    assert count == 1


def test_synchronize_progress_bar(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    master = tmp_path / "master.db"
    replica1 = tmp_path / "r1.db"
    replica2 = tmp_path / "r2.db"
    log_db = tmp_path / "enterprise_assets.db"
    initialize_database(log_db)
    for db in [master, replica1, replica2]:
        with sqlite3.connect(db) as conn:
            conn.execute("CREATE TABLE t (id INTEGER)")
            conn.execute("INSERT INTO t (id) VALUES (1)")

    bars: List[DummyTqdm] = []

    def dummy_tqdm(*args: Any, **kwargs: Any) -> DummyTqdm:
        bar = DummyTqdm(*args, **kwargs)
        bars.append(bar)
        return bar

    monkeypatch.setattr("scripts.database.unified_database_management_system.tqdm", dummy_tqdm)

    synchronize_databases(master, [replica1, replica2], log_db=log_db)

    assert bars and bars[0].updates == 2
    with sqlite3.connect(replica1) as conn:
        assert conn.execute("SELECT COUNT(*) FROM t").fetchone()[0] == 1
    with sqlite3.connect(replica2) as conn:
        assert conn.execute("SELECT COUNT(*) FROM t").fetchone()[0] == 1
    with sqlite3.connect(log_db) as conn:
        count = conn.execute(
            "SELECT COUNT(*) FROM cross_database_sync_operations"
        ).fetchone()[0]
    assert count == 2

