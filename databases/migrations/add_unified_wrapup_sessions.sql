CREATE TABLE IF NOT EXISTS unified_wrapup_sessions (
    session_id TEXT PRIMARY KEY,
    start_time TEXT,
    end_time TEXT,
    status TEXT,
    files_organized INTEGER,
    configs_validated INTEGER,
    scripts_modularized INTEGER,
    root_files_remaining INTEGER,
    compliance_score REAL,
    validation_results TEXT,
    error_details TEXT
);
CREATE INDEX IF NOT EXISTS idx_unified_wrapup_status ON unified_wrapup_sessions(status);
