-- Migration script upgrading schema from v1 to v2

-- Add last_login column to web_users if it does not exist
ALTER TABLE web_users ADD COLUMN IF NOT EXISTS last_login TEXT;

-- Add is_active column to web_pages if it does not exist and default to active
ALTER TABLE web_pages ADD COLUMN IF NOT EXISTS is_active INTEGER DEFAULT 1;

-- Ensure existing pages are marked active
UPDATE web_pages SET is_active = 1 WHERE is_active IS NULL;
