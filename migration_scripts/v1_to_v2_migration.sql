-- Upgrade schema from v1 to v2 using database-first approach
BEGIN TRANSACTION;
ALTER TABLE ui_state ADD COLUMN updated_at TEXT;
COMMIT;
