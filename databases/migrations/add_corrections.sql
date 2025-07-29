CREATE TABLE IF NOT EXISTS corrections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT,
    rationale TEXT,
    compliance_score REAL,
    rollback_reference TEXT,
    ts TEXT
);
CREATE INDEX IF NOT EXISTS idx_corrections_ts ON corrections(ts);
