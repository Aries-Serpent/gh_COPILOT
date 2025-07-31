CREATE TABLE IF NOT EXISTS cross_link_summary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    actions INTEGER,
    links INTEGER,
    summary_path TEXT,
    timestamp TEXT NOT NULL
);
