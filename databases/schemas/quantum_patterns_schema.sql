-- Schema for quantum learning patterns
CREATE TABLE IF NOT EXISTS pattern_registry (
    id INTEGER PRIMARY KEY,
    pattern_name TEXT NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS pattern_usage (
    pattern_id INTEGER,
    usage_count INTEGER DEFAULT 0,
    last_used TEXT,
    FOREIGN KEY(pattern_id) REFERENCES pattern_registry(id)
);
