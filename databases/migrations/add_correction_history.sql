CREATE TABLE IF NOT EXISTS correction_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    session_id TEXT NOT NULL,
    file_path TEXT NOT NULL,
    action TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    details TEXT
);
CREATE INDEX IF NOT EXISTS idx_correction_history_user_id ON correction_history(user_id);
CREATE INDEX IF NOT EXISTS idx_correction_history_session_id ON correction_history(session_id);
CREATE INDEX IF NOT EXISTS idx_correction_history_file_path ON correction_history(file_path);
CREATE INDEX IF NOT EXISTS idx_correction_history_timestamp ON correction_history(timestamp);
