CREATE TABLE IF NOT EXISTS correction_history (
    session_id TEXT NOT NULL,
    file_path TEXT NOT NULL,
    violation_code TEXT NOT NULL,
    fix_applied TEXT NOT NULL,
    timestamp TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_correction_history_session_id ON correction_history(session_id);
CREATE INDEX IF NOT EXISTS idx_correction_history_file_path ON correction_history(file_path);
CREATE INDEX IF NOT EXISTS idx_correction_history_timestamp ON correction_history(timestamp);
