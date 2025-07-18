import sqlite3
from pathlib import Path

import py7zr

from scripts.database.complete_consolidation_orchestrator import \
    export_table_to_7z


def test_export_table_to_7z(tmp_path: Path) -> None:
    db = tmp_path / "sample.db"
    with sqlite3.connect(db) as conn:
        conn.execute("CREATE TABLE t (id INTEGER)")
        conn.executemany("INSERT INTO t (id) VALUES (?)", [(i,) for i in range(5)])
        conn.commit()

    archive = export_table_to_7z(db, "t", tmp_path)
    assert archive.exists()
    with py7zr.SevenZipFile(archive, "r") as zf:
        names = zf.getnames()
    assert any(name.endswith("t.csv") for name in names)
