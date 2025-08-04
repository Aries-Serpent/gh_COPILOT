from datetime import datetime, timezone

import sqlite3

from scripts.database.cross_database_reconciler import reconcile_once
from scripts.database.cross_database_sync_logger import log_sync_operation
from scripts.database.unified_database_initializer import initialize_database


def test_reconcile_once_fills_missing_rows(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(
        "enterprise_modules.compliance.validate_enterprise_operation", lambda: True
    )
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    db1 = tmp_path / "db1.db"
    db2 = tmp_path / "db2.db"
    initialize_database(db1)
    initialize_database(db2)
    for db in (db1, db2):
        with sqlite3.connect(db) as conn:
            conn.execute("DELETE FROM cross_database_sync_operations")
            conn.commit()
    start = datetime.now(timezone.utc)
    log_sync_operation(db1, "op1", start_time=start)

    reconcile_once([db1, db2])

    with sqlite3.connect(db1) as conn:
        count1 = conn.execute(
            "SELECT COUNT(*) FROM cross_database_sync_operations"
        ).fetchone()[0]
    with sqlite3.connect(db2) as conn:
        count2 = conn.execute(
            "SELECT COUNT(*) FROM cross_database_sync_operations"
        ).fetchone()[0]
    assert count1 == count2
    assert count1 == 2

