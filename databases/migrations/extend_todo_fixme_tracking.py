import sqlite3


def _has_col(conn: sqlite3.Connection, table: str, col: str) -> bool:
    return any(r[1] == col for r in conn.execute(f"PRAGMA table_info({table})"))


def upgrade(conn: sqlite3.Connection) -> None:
    if not _has_col(conn, "todo_fixme_tracking", "status"):
        conn.execute(
            "ALTER TABLE todo_fixme_tracking ADD COLUMN status TEXT DEFAULT 'open'"
        )
    if not _has_col(conn, "todo_fixme_tracking", "removal_id"):
        conn.execute(
            "ALTER TABLE todo_fixme_tracking ADD COLUMN removal_id INTEGER REFERENCES placeholder_removals(id)"
        )
    conn.commit()
