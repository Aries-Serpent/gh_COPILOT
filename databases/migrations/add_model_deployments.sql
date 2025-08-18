CREATE TABLE IF NOT EXISTS model_deployments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_name TEXT NOT NULL,
    version TEXT NOT NULL,
    stage TEXT,
    status TEXT NOT NULL,
    artifact_path TEXT NOT NULL,
    artifact_hashes TEXT NOT NULL,
    created_at TEXT NOT NULL
);

