-- Prepare database for quantum processing features

-- Create table for quantum jobs if it does not exist
CREATE TABLE IF NOT EXISTS quantum_jobs (
    id INTEGER PRIMARY KEY,
    job_name TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Insert a default job ensuring idempotency
INSERT OR IGNORE INTO quantum_jobs (id, job_name, status)
VALUES (1, 'initial_setup', 'completed');
