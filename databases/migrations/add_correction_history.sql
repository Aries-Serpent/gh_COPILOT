<<<<<<< HEAD
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
=======
DROP TABLE IF EXISTS correction_history;
CREATE TABLE correction_history (
    session_id TEXT NOT NULL,
    file_path TEXT NOT NULL,
    violation_code TEXT NOT NULL,
    fix_applied TEXT NOT NULL,
    timestamp TEXT NOT NULL
);
>>>>>>> 072d1e7e (Nuclear fix: Complete repository rebuild - 2025-07-14 22:31:03)
CREATE INDEX IF NOT EXISTS idx_correction_history_session_id ON correction_history(session_id);
CREATE INDEX IF NOT EXISTS idx_correction_history_file_path ON correction_history(file_path);
CREATE INDEX IF NOT EXISTS idx_correction_history_timestamp ON correction_history(timestamp);
