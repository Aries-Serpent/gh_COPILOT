-- Add version column for tracking documentation revisions
ALTER TABLE documentation_assets ADD COLUMN version INTEGER NOT NULL DEFAULT 1;
