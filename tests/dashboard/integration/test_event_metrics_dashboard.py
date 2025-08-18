import sqlite3

from scripts.monitoring import database_event_monitor as dem


def test_event_metrics_dashboard(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "enterprise_modules.compliance.validate_enterprise_operation", lambda: True
    )
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    updates = []
    monkeypatch.setattr(dem, "_update_dashboard", lambda payload: updates.append(payload))

    db1 = tmp_path / "db1.db"
    db2 = tmp_path / "db2.db"
    for db, count in [(db1, 1), (db2, 2)]:
        with sqlite3.connect(db) as conn:
            conn.execute("CREATE TABLE cross_database_sync_operations (id INTEGER)")
            for _ in range(count):
                conn.execute("INSERT INTO cross_database_sync_operations VALUES (1)")
            conn.commit()

    analytics = tmp_path / "databases" / "analytics.db"
    analytics.parent.mkdir()
    dem.collect_metrics([db1, db2], analytics)

    assert {"db_path": str(db1), "event_count": 1} in updates
    assert {"db_path": str(db2), "event_count": 2} in updates

