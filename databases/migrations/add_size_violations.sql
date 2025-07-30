CREATE TABLE IF NOT EXISTS size_violations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    db TEXT,
    table_name TEXT,
    size_mb REAL,
    threshold REAL,
    timestamp TEXT
);
