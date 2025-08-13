from datetime import datetime, timezone
import logging

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


def test_conflict_triggers_rollback(tmp_path, monkeypatch, caplog) -> None:
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
    log_sync_operation(db1, "op_good", start_time=start)
    log_sync_operation(db1, "op_conflict", start_time=start)
    with sqlite3.connect(db1) as conn:
        conflict_row = conn.execute(
            "SELECT operation, status, start_time, duration, timestamp FROM cross_database_sync_operations WHERE operation=?",
            ("op_conflict",),
        ).fetchone()
    with sqlite3.connect(db2) as conn:
        conn.execute(
            "INSERT INTO cross_database_sync_operations (operation, status, start_time, duration, timestamp) VALUES (?, ?, ?, ?, ?)",
            (conflict_row[0], "FAILED", conflict_row[2], conflict_row[3], conflict_row[4]),
        )
        conn.commit()

    with caplog.at_level(logging.ERROR):
        reconcile_once([db1, db2])

    with sqlite3.connect(db2) as conn:
        rows = conn.execute(
            "SELECT operation, status FROM cross_database_sync_operations"
        ).fetchall()
    rows = [r for r in rows if r[0] != "reconcile_databases"]
    assert rows == [("op_conflict", "FAILED")]
    assert any("reconcile_rollback" in r.getMessage() for r in caplog.records)

