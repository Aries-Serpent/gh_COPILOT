-- gh_COPILOT: initial schema for analytics/compliance
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS compliance_models (
  model_id TEXT PRIMARY KEY,
  weights_json TEXT NOT NULL,
  min_score REAL NOT NULL,
  effective_from TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS score_inputs (
  run_id TEXT PRIMARY KEY,
  lint REAL NOT NULL,
  tests REAL NOT NULL,
  placeholders REAL NOT NULL,
  sessions REAL NOT NULL,
  model_id TEXT NOT NULL,
  ts TEXT NOT NULL,
  FOREIGN KEY (model_id) REFERENCES compliance_models(model_id)
);
CREATE INDEX IF NOT EXISTS idx_score_inputs_ts ON score_inputs(ts);

CREATE TABLE IF NOT EXISTS score_snapshots (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  branch TEXT NOT NULL,
  score REAL NOT NULL,
  model_id TEXT NOT NULL,
  inputs_json TEXT NOT NULL,
  ts TEXT NOT NULL,
  FOREIGN KEY (model_id) REFERENCES compliance_models(model_id)
);
CREATE INDEX IF NOT EXISTS idx_score_snapshots_branch_ts ON score_snapshots(branch, ts DESC);

CREATE TABLE IF NOT EXISTS placeholder_tasks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  file TEXT NOT NULL,
  line INTEGER NOT NULL,
  kind TEXT NOT NULL,
  sha TEXT,
  ts TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'open'
);
CREATE INDEX IF NOT EXISTS idx_placeholder_tasks_status_ts ON placeholder_tasks(status, ts DESC);
