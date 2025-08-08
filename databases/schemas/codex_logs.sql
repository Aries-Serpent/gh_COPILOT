-- Schema for Codex action logs
CREATE TABLE IF NOT EXISTS codex_logs (
    id INTEGER PRIMARY KEY,
    session_id TEXT,
    timestamp TEXT,
    action TEXT,
    statement TEXT,
    metadata TEXT
);

