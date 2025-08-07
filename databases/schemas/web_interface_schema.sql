-- Schema for web interface components

-- Create table for storing available web pages
CREATE TABLE IF NOT EXISTS web_pages (
    id INTEGER PRIMARY KEY,
    page_name TEXT UNIQUE NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Create table for tracking web users
CREATE TABLE IF NOT EXISTS web_users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
