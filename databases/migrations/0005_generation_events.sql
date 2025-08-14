PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS generation_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  kind TEXT NOT NULL,
  source TEXT NOT NULL,
  target_path TEXT NOT NULL,
  template_id TEXT,
  inputs_json TEXT,
  ts TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_generation_events_ts ON generation_events(ts DESC);
