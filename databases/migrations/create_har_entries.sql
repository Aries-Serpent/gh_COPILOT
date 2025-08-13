DROP TABLE IF EXISTS har_entries;
CREATE TABLE har_entries (
    id INTEGER PRIMARY KEY,
    path TEXT NOT NULL,
    content_hash TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL,
    metrics TEXT
);
