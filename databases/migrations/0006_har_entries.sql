PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS har_entries (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  path TEXT NOT NULL,
  sha256 TEXT,
  content_hash TEXT,
  created_at TEXT NOT NULL,
  metrics_json TEXT,
  metrics TEXT
);

-- Unique index using coalesced hash to remain compatible with legacy content_hash-only rows
CREATE UNIQUE INDEX IF NOT EXISTS ux_har_entries_path_hash
  ON har_entries(path, COALESCE(sha256, content_hash));
