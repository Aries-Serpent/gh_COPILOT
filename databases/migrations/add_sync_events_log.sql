CREATE TABLE IF NOT EXISTS sync_events_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT,
    target TEXT,
    ts TEXT
);
