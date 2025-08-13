# idempotent migration: add 'version' to documentation_assets if present & missing
import sqlite3

def upgrade(conn: sqlite3.Connection) -> None:
    cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='documentation_assets'")
    if not cur.fetchone():
        # Table may not exist on fresh DBs — safe no-op
        return
    cols = {r[1] for r in conn.execute("PRAGMA table_info(documentation_assets)")}
    if "version" not in cols:
        conn.execute("ALTER TABLE documentation_assets ADD COLUMN version INTEGER NOT NULL DEFAULT 1")
        conn.commit()
