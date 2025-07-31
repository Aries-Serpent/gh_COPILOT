import sqlite3
from pathlib import Path

from scripts.regenerated.cross_database_aggregation_implementation import (
    EnterpriseDatabaseProcessor,
)


def _make_db(path: Path, table: str, rows: int) -> None:
    with sqlite3.connect(path) as conn:
        conn.execute(f"CREATE TABLE {table} (id INTEGER)")
        for i in range(rows):
            conn.execute(f"INSERT INTO {table} (id) VALUES (?)", (i,))


def test_process_operations(tmp_path: Path) -> None:
    db_main = tmp_path / "main.db"
    db_a = tmp_path / "a.db"
    db_b = tmp_path / "b.db"

    _make_db(db_main, "main_table", 1)
    _make_db(db_a, "table_a", 2)
    _make_db(db_b, "table_b", 3)

    processor = EnterpriseDatabaseProcessor(str(db_main))
    assert processor.execute_processing()

    with sqlite3.connect(db_main) as conn:
        rows = conn.execute("SELECT db_name, table_name, row_count FROM cross_database_summary").fetchall()

    summary = {(r[0], r[1]): r[2] for r in rows}
    assert summary[("a.db", "table_a")] == 2
    assert summary[("b.db", "table_b")] == 3
