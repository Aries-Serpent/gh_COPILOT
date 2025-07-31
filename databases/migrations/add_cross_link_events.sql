CREATE TABLE IF NOT EXISTS cross_link_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT NOT NULL,
    linked_path TEXT NOT NULL,
    timestamp TEXT NOT NULL
);
