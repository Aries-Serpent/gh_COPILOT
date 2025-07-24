import sqlite3
from pathlib import Path

from scripts.database.add_code_audit_log import add_table


def test_add_code_audit_log(tmp_path: Path) -> None:
    db = tmp_path / "analytics.db"
    with sqlite3.connect(db) as conn:
        conn.execute("CREATE TABLE placeholder_audit (id INTEGER)")
    # run migration twice to ensure idempotence
    add_table(db)
    add_table(db)
    with sqlite3.connect(db) as conn:
        conn.execute(
            "INSERT INTO code_audit_log (file_path, line_number, placeholder_type, context, timestamp)"
            " VALUES ('f', 1, 'TODO', 'ctx', 'ts')"
        )
        rows = conn.execute("SELECT file_path FROM code_audit_log").fetchall()
    assert rows
