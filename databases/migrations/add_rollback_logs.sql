CREATE TABLE IF NOT EXISTS rollback_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    target TEXT NOT NULL,
    backup TEXT,
    timestamp TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_rollback_logs_timestamp
    ON rollback_logs(timestamp);

