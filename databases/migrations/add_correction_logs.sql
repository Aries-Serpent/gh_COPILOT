CREATE TABLE IF NOT EXISTS correction_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event TEXT,
    doc_id TEXT,
    path TEXT,
    asset_type TEXT,
    compliance_score REAL,
    timestamp TEXT
);
CREATE INDEX IF NOT EXISTS idx_correction_logs_timestamp
    ON correction_logs(timestamp);
