ALTER TABLE todo_fixme_tracking ADD COLUMN status TEXT DEFAULT 'open';
ALTER TABLE todo_fixme_tracking ADD COLUMN removal_id INTEGER REFERENCES placeholder_removals(id);
