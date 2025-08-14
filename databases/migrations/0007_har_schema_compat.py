# Idempotent compat migration for har_entries: ensure both sha256/content_hash and metrics/metrics_json exist
import sqlite3

def _cols(conn: sqlite3.Connection, table: str) -> set[str]:
    return {r[1] for r in conn.execute(f"PRAGMA table_info({table})")}

def upgrade(conn: sqlite3.Connection) -> None:
    conn.execute("CREATE TABLE IF NOT EXISTS har_entries(id INTEGER PRIMARY KEY AUTOINCREMENT, path TEXT NOT NULL, created_at TEXT NOT NULL)")
    cols = _cols(conn, "har_entries")
    if "sha256" not in cols:
        conn.execute("ALTER TABLE har_entries ADD COLUMN sha256 TEXT")
    if "content_hash" not in cols:
        conn.execute("ALTER TABLE har_entries ADD COLUMN content_hash TEXT")
    if "metrics_json" not in cols:
        conn.execute("ALTER TABLE har_entries ADD COLUMN metrics_json TEXT")
    if "metrics" not in cols:
        conn.execute("ALTER TABLE har_entries ADD COLUMN metrics TEXT")
    # Backfill: prefer sha256->content_hash if present
    conn.execute("UPDATE har_entries SET content_hash = COALESCE(content_hash, sha256)")
    # Backfill metrics: prefer metrics_json -> metrics as text if empty
    conn.execute("UPDATE har_entries SET metrics = COALESCE(metrics, metrics_json)")
    # Recreate unique index
    conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS ux_har_entries_path_hash ON har_entries(path, COALESCE(sha256, content_hash))")
    conn.commit()
