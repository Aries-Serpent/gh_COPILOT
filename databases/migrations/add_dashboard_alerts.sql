CREATE TABLE IF NOT EXISTS dashboard_alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    db TEXT,
    table_name TEXT,
    size_mb REAL,
    threshold REAL,
    timestamp TEXT
);
