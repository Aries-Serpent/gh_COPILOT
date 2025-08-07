-- Prepare database for quantum pattern module
BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS quantum_seed (
    id INTEGER PRIMARY KEY,
    seed_value TEXT NOT NULL
);
COMMIT;
