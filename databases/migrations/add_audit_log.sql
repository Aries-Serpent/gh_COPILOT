CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    db_name TEXT,
    details TEXT,
    ts TEXT
);
