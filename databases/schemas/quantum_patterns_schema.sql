-- Schema capturing reusable quantum patterns

-- Create table for defining quantum patterns
CREATE TABLE IF NOT EXISTS quantum_patterns (
    id INTEGER PRIMARY KEY,
    pattern_name TEXT UNIQUE NOT NULL,
    description TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Create table for tracking pattern usage metrics
CREATE TABLE IF NOT EXISTS quantum_pattern_usage (
    id INTEGER PRIMARY KEY,
    pattern_id INTEGER NOT NULL,
    usage_count INTEGER DEFAULT 0,
    last_used TEXT,
    FOREIGN KEY (pattern_id) REFERENCES quantum_patterns(id)
);
