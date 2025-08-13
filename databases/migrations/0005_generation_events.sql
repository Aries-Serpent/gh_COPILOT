PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS generation_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  kind TEXT NOT NULL,          -- 'docs' | 'scripts'
  source TEXT NOT NULL,        -- e.g., 'documentation.db' or 'production.db'
  target_path TEXT NOT NULL,   -- file written
  template_id TEXT,            -- optional
  inputs_json TEXT,            -- parameters/metadata
  ts TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_generation_events_ts ON generation_events(ts DESC);
