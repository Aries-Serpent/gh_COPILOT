PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS ingest_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  kind TEXT NOT NULL,          -- 'har' | 'docs' | 'templates' | ...
  path TEXT NOT NULL,
  sha256 TEXT NOT NULL,
  metrics_json TEXT,
  ts TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_ingest_events_ts ON ingest_events(ts DESC);
