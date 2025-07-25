CREATE TABLE IF NOT EXISTS code_audit_history (
    id INTEGER PRIMARY KEY,
    audit_entry TEXT NOT NULL,
    user TEXT NOT NULL,
    timestamp TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_code_audit_history_timestamp ON code_audit_history(timestamp);
CREATE INDEX IF NOT EXISTS idx_code_audit_history_user ON code_audit_history(user);
