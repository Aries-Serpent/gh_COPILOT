CREATE TABLE IF NOT EXISTS cross_link_suggestions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT NOT NULL,
    suggested_link TEXT NOT NULL,
    score REAL,
    timestamp TEXT NOT NULL
);
