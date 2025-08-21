-- Upgrade schema from v1 to v2 using database-first approach
BEGIN TRANSACTION;
ALTER TABLE ui_state ADD COLUMN updated_at TEXT;
ALTER TABLE enterprise_metrics ADD COLUMN metric_unit TEXT;
COMMIT;
