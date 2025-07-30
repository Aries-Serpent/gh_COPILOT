CREATE TABLE IF NOT EXISTS todo_fixme_tracking (
    file_path TEXT,
    line_number INTEGER,
    placeholder_type TEXT,
    context TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    resolved BOOLEAN DEFAULT 0,
    resolved_timestamp DATETIME,
    status TEXT DEFAULT 'open',
    removal_id INTEGER REFERENCES placeholder_removals(id)
);
CREATE INDEX IF NOT EXISTS idx_todo_fixme_tracking_path_line ON todo_fixme_tracking(file_path, line_number);
