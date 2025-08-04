CREATE TABLE IF NOT EXISTS corrections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT,
    rationale TEXT,
    correction_type TEXT,
    compliance_score REAL,
    compliance_delta REAL,
    rollback_reference TEXT,
    session_id TEXT,
    ts TEXT
);
CREATE INDEX IF NOT EXISTS idx_corrections_ts ON corrections(ts);
