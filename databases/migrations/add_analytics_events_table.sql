CREATE TABLE IF NOT EXISTS analytics_events (
  run_id  TEXT NOT NULL,
  kind    TEXT NOT NULL,
  payload TEXT NOT NULL,
  ts      TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
);
