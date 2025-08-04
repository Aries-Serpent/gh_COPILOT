CREATE TABLE IF NOT EXISTS legacy_cleanup_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file TEXT NOT NULL,
    action TEXT NOT NULL,
    reason TEXT,
    timestamp TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_legacy_cleanup_log_timestamp
    ON legacy_cleanup_log(timestamp);
