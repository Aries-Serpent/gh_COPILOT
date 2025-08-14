-- [SQL]: har_entries schema
> Generated: 2025-08-14 02:47:12 | Author: mbaetiong

PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS har_entries (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  path TEXT NOT NULL,
  sha256 TEXT NOT NULL,
  created_at TEXT NOT NULL,
  metrics_json TEXT
);
CREATE UNIQUE INDEX IF NOT EXISTS ux_har_entries_path_sha ON har_entries(path, sha256);
