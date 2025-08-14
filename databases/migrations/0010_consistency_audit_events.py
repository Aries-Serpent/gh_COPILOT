import sqlite3

def _has_table(conn: sqlite3.Connection, name: str) -> bool:
    row = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (name,)
    ).fetchone()
    return row is not None


def upgrade(conn: sqlite3.Connection) -> None:
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA busy_timeout=10000;")
    # Event log capturing each audit execution and its findings
    if not _has_table(conn, "consistency_audit_events"):
        conn.execute(
            """
            CREATE TABLE consistency_audit_events (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              started_at TEXT NOT NULL,
              finished_at TEXT NOT NULL,
              scanned_paths TEXT NOT NULL,
              missing_count INTEGER NOT NULL,
              stale_count INTEGER NOT NULL,
              regenerated_count INTEGER NOT NULL,
              reingested_count INTEGER NOT NULL,
              details_json TEXT,
              status TEXT NOT NULL DEFAULT 'ok'
            );
            """
        )
    # Helpful index for dashboard/filters
    conn.execute(
        "CREATE INDEX IF NOT EXISTS ix_consistency_audit_events_started_at "
        "ON consistency_audit_events(started_at)"
    )
    conn.commit()
