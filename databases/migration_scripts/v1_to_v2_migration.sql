-- Migration script upgrading schema from v1 to v2

-- SQLite does not support the "IF NOT EXISTS" clause for ADD COLUMN.
-- The following statements assume the columns do not yet exist.
ALTER TABLE web_users ADD COLUMN last_login TEXT;

ALTER TABLE web_pages ADD COLUMN is_active INTEGER DEFAULT 1;
ALTER TABLE enterprise_metrics ADD COLUMN metric_unit TEXT;

-- Ensure existing pages are marked active
UPDATE web_pages SET is_active = 1 WHERE is_active IS NULL;
