-- Initialize tables for enterprise authentication

-- Create table defining enterprise roles
CREATE TABLE IF NOT EXISTS enterprise_roles (
    id INTEGER PRIMARY KEY,
    role_name TEXT UNIQUE NOT NULL
);

-- Create table capturing enterprise users
CREATE TABLE IF NOT EXISTS enterprise_users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    role_id INTEGER,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES enterprise_roles(id)
);

-- Insert default admin role
INSERT OR IGNORE INTO enterprise_roles (id, role_name)
VALUES (1, 'admin');

-- Insert default admin user referencing admin role
INSERT OR IGNORE INTO enterprise_users (id, username, role_id)
VALUES (1, 'admin', 1);
