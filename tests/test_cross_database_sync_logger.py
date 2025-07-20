import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path

from scripts.database.cross_database_sync_logger import log_sync_operation


def test_log_sync_operation(tmp_path: Path) -> None:
    db_path = tmp_path / "enterprise_assets.db"
    start = datetime.now(timezone.utc)
    time.sleep(0.01)
    log_sync_operation(db_path, "test_op", status="SUCCESS", start_time=start)
    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            "SELECT operation, status, start_time, duration, timestamp FROM cross_database_sync_operations"
        ).fetchone()
    assert row[0] == "test_op"
    assert row[1] == "SUCCESS"
    assert row[2] == start.isoformat()
    assert row[3] > 0

