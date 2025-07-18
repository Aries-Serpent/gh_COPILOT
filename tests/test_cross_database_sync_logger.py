import sqlite3
from pathlib import Path

from scripts.database.cross_database_sync_logger import log_sync_operation


def test_log_sync_operation(tmp_path: Path) -> None:
    db_path = tmp_path / "enterprise_assets.db"
    log_sync_operation(db_path, "test_op")
    with sqlite3.connect(db_path) as conn:
        count = conn.execute(
            "SELECT COUNT(*) FROM cross_database_sync_operations"
        ).fetchone()[0]
    assert count == 1
