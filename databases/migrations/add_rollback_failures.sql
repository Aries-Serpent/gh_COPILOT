CREATE TABLE IF NOT EXISTS rollback_failures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event TEXT,
    module TEXT,
    level TEXT,
    target TEXT NOT NULL,
    details TEXT,
    timestamp TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_rollback_failures_timestamp
    ON rollback_failures(timestamp);
