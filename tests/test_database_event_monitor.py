import sqlite3
from datetime import datetime, timezone

from scripts.database.cross_database_sync_logger import log_sync_operation
from scripts.database.unified_database_initializer import initialize_database
from scripts.monitoring.database_event_monitor import collect_metrics


def test_collect_metrics_records_counts(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(
        "enterprise_modules.compliance.validate_enterprise_operation", lambda: True
    )
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    db1 = tmp_path / "db1.db"
    db2 = tmp_path / "db2.db"
    analytics = tmp_path / "analytics.db"
    initialize_database(db1)
    initialize_database(db2)
    start = datetime.now(timezone.utc)
    log_sync_operation(db1, "op1", start_time=start)

    collect_metrics([db1, db2], analytics)

    with sqlite3.connect(analytics) as conn:
        count = conn.execute("SELECT COUNT(*) FROM event_rate_metrics").fetchone()[0]
    assert count == 2

