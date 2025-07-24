CREATE TABLE IF NOT EXISTS code_audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT NOT NULL,
    line_number INTEGER NOT NULL,
    placeholder_type TEXT NOT NULL,
    context TEXT,
    timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_code_audit_log_file ON code_audit_log(file_path);
CREATE INDEX IF NOT EXISTS idx_code_audit_log_time ON code_audit_log(timestamp);
