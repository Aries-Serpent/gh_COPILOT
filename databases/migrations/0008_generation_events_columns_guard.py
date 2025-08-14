import sqlite3


def _has_col(conn: sqlite3.Connection, table: str, col: str) -> bool:
    return any(r[1] == col for r in conn.execute(f"PRAGMA table_info({table})"))


def upgrade(conn: sqlite3.Connection) -> None:
    if not _has_col(conn, "generation_events", "status"):
        conn.execute(
            "ALTER TABLE generation_events ADD COLUMN status TEXT DEFAULT 'ok'"
        )
    if not _has_col(conn, "generation_events", "error_message"):
        conn.execute(
            "ALTER TABLE generation_events ADD COLUMN error_message TEXT"
        )
    conn.commit()
