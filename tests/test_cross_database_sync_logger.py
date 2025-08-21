import sqlite3
import time
import datetime
from pathlib import Path

from scripts.database.cross_database_sync_logger import log_sync_operation
from scripts.database.unified_database_initializer import initialize_database


def test_log_sync_operation(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(
        "enterprise_modules.compliance.validate_enterprise_operation",
        lambda: None,
    )
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    db_path = tmp_path / "enterprise_assets.db"
    start = datetime.datetime.now(datetime.timezone.utc)
    time.sleep(0.01)
    log_sync_operation(db_path, "test_op", status="SUCCESS", start_time=start)
    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            "SELECT operation, status, start_time, duration, timestamp FROM cross_database_sync_operations ORDER BY id DESC"
        ).fetchone()
    assert row[0] == "test_op"
    assert row[1] == "SUCCESS"
    assert row[2] == start.isoformat()
    assert row[3] > 0


def test_log_sync_operation_accepts_naive_datetime(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(
        "enterprise_modules.compliance.validate_enterprise_operation",
        lambda: None,
    )
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    db_path = tmp_path / "enterprise_assets.db"
    start = datetime.datetime.now(datetime.timezone.utc)
    log_sync_operation(db_path, "test_op", status="SUCCESS", start_time=start)
    with sqlite3.connect(db_path) as conn:
        row = conn.execute("SELECT start_time FROM cross_database_sync_operations ORDER BY id DESC").fetchone()
    assert row[0] == start.replace(tzinfo=timezone.utc).isoformat()


def test_log_sync_operation_multiple_databases(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(
        "enterprise_modules.compliance.validate_enterprise_operation",
        lambda: None,
    )
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    db1 = tmp_path / "db1.db"
    db2 = tmp_path / "db2.db"
    initialize_database(db1)
    initialize_database(db2)
    before = []
    for db in (db1, db2):
        with sqlite3.connect(db) as conn:
            before.append(conn.execute("SELECT COUNT(*) FROM cross_database_sync_operations").fetchone()[0])
    start = datetime.datetime.now(datetime.timezone.utc)
    log_sync_operation([db1, db2], "multi", start_time=start)
    for idx, db in enumerate((db1, db2)):
        with sqlite3.connect(db) as conn:
            after = conn.execute("SELECT COUNT(*) FROM cross_database_sync_operations").fetchone()[0]
        assert after == before[idx] + 1


def test_log_sync_operation_with_analytics(tmp_path: Path, monkeypatch) -> None:
    """Verify analytics event emission via log_event."""
    monkeypatch.setattr(
        "enterprise_modules.compliance.validate_enterprise_operation",
        lambda: None,
    )
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    analytics_db = tmp_path / "analytics.db"
    monkeypatch.setenv("ANALYTICS_DB", str(analytics_db))
    db_path = tmp_path / "enterprise_assets.db"
    initialize_database(db_path)
    log_sync_operation(db_path, "analytics_op")
    with sqlite3.connect(analytics_db) as conn:
        row = conn.execute("SELECT module, description FROM event_log ORDER BY id DESC").fetchone()
    assert row == ("cross_database_sync_logger", "analytics_op")
