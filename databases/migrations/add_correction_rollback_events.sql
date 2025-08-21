CREATE TABLE IF NOT EXISTS correction_rollback_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,
    target TEXT NOT NULL,
    backup TEXT,
    status TEXT,
    timestamp TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_correction_rollback_events_timestamp
    ON correction_rollback_events(timestamp);
