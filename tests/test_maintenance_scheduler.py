import sqlite3
from pathlib import Path

from scripts.database.maintenance_scheduler import run_cycle
from scripts.database.unified_database_initializer import initialize_database


def test_run_cycle(tmp_path: Path) -> None:
    db_dir = tmp_path / "databases"
    docs_dir = tmp_path / "documentation"
    db_dir.mkdir()
    docs_dir.mkdir()

    master = db_dir / "enterprise_assets.db"
    replica = db_dir / "replica.db"
    log_db = master
    initialize_database(log_db)

    with sqlite3.connect(master) as conn:
        conn.execute("CREATE TABLE t (id INTEGER)")
        conn.execute("INSERT INTO t (id) VALUES (1)")

    list_file = docs_dir / "CONSOLIDATED_DATABASE_LIST.md"
    list_file.write_text(
        "- enterprise_assets.db  # Size: 0.01 MB\n"
        "- replica.db  # Size: 0.01 MB\n"
    )

    run_cycle(tmp_path)

    with sqlite3.connect(replica) as conn:
        count = conn.execute("SELECT COUNT(*) FROM t").fetchone()[0]
    assert count == 1
