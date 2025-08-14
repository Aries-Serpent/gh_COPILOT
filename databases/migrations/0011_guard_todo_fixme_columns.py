from __future__ import annotations
import sqlite3

def apply(conn: sqlite3.Connection) -> None:
    try:
        cols = {r[1] for r in conn.execute("PRAGMA table_info('todo_fixme_tracking')")}
    except sqlite3.Error:
        return
    if 'status' not in cols:
        conn.execute("ALTER TABLE todo_fixme_tracking ADD COLUMN status TEXT DEFAULT 'open'")
    if 'removal_id' not in cols:
        conn.execute("ALTER TABLE todo_fixme_tracking ADD COLUMN removal_id INTEGER")
