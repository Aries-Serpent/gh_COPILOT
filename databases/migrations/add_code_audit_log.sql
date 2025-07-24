CREATE TABLE IF NOT EXISTS code_audit_log (
    id INTEGER PRIMARY KEY,
    file_path TEXT NOT NULL,
    line_number INTEGER,
    placeholder_type TEXT,
    context TEXT,
    timestamp TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_code_audit_log_file_path ON code_audit_log(file_path);
CREATE INDEX IF NOT EXISTS idx_code_audit_log_timestamp ON code_audit_log(timestamp);
