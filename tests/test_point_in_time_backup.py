import sqlite3

from scripts.database.unified_database_initializer import initialize_database
from scripts.disaster_recovery.point_in_time_backup import (
    create_snapshot,
    restore_snapshot,
)


def test_snapshot_and_restore(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(
        "enterprise_modules.compliance.validate_enterprise_operation", lambda: True
    )
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(tmp_path / "backups"))
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))

    src = tmp_path / "src.db"
    initialize_database(src)
    with sqlite3.connect(src) as conn:
        conn.execute("DELETE FROM cross_database_sync_operations")
        conn.execute(
            "INSERT INTO cross_database_sync_operations (operation, status, start_time, duration, timestamp) VALUES ('a','b','c',1,'d')"
        )
        conn.commit()

    backup = create_snapshot(src)
    restored = tmp_path / "restored.db"
    restore_snapshot(backup, restored)

    with sqlite3.connect(restored) as conn:
        count = conn.execute(
            "SELECT COUNT(*) FROM cross_database_sync_operations"
        ).fetchone()[0]
    assert count == 1

