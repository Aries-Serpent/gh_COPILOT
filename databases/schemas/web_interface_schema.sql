-- Schema for web GUI data
CREATE TABLE IF NOT EXISTS ui_state (
    id INTEGER PRIMARY KEY,
    component TEXT NOT NULL,
    value TEXT
);

CREATE TABLE IF NOT EXISTS user_preferences (
    user_id INTEGER PRIMARY KEY,
    theme TEXT DEFAULT 'light',
    notifications BOOLEAN DEFAULT 1
);
