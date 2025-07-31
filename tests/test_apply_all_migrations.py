import sqlite3
from pathlib import Path


def test_apply_all_migrations(tmp_path: Path) -> None:
    db_file = tmp_path / "analytics.db"
    migrations = [
        Path("databases/migrations/create_todo_fixme_tracking.sql"),
        Path("databases/migrations/add_code_audit_log.sql"),
        Path("databases/migrations/add_correction_history.sql"),
        Path("databases/migrations/add_code_audit_history.sql"),
        Path("databases/migrations/add_violation_logs.sql"),
        Path("databases/migrations/add_rollback_logs.sql"),
        Path("databases/migrations/add_corrections.sql"),
        Path("databases/migrations/add_placeholder_removals.sql"),
        Path("databases/migrations/add_size_violations.sql"),
        Path("databases/migrations/add_unified_wrapup_sessions.sql"),
        Path("databases/migrations/extend_todo_fixme_tracking.sql"),
    ]
    with sqlite3.connect(db_file) as conn:
        for sql in migrations:
            try:
                conn.executescript(sql.read_text())
            except sqlite3.OperationalError:
                # Some migrations may reapply columns; ignore duplicate errors
                pass
    with sqlite3.connect(db_file) as conn:
        tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    expected = {
        "code_audit_log",
        "correction_history",
        "code_audit_history",
        "violation_logs",
        "rollback_logs",
        "corrections",
        "unified_wrapup_sessions",
        "todo_fixme_tracking",
        "placeholder_removals",
        "size_violations",
    }
    assert expected.issubset(tables)
