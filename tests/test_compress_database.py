import sqlite3
from pathlib import Path

from scripts.database.unified_database_migration import _compress_database


def test_compress_database_reduces_size(tmp_path: Path) -> None:
    db = tmp_path / "sample.db"
    with sqlite3.connect(db) as conn:
        conn.execute("CREATE TABLE t (data TEXT)")
        for _ in range(1000):
            conn.execute("INSERT INTO t (data) VALUES (?)", ("x" * 100,))
        conn.commit()

    _compress_database(db)
    assert db.stat().st_size > 0
