-- Schema for asset ingestion tables

CREATE TABLE IF NOT EXISTS documentation_assets (
    id INTEGER PRIMARY KEY,
    doc_path TEXT NOT NULL,
    content_hash TEXT NOT NULL UNIQUE,
    version INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    modified_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS template_assets (
    id INTEGER PRIMARY KEY,
    template_path TEXT NOT NULL,
    content_hash TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS pattern_assets (
    id INTEGER PRIMARY KEY,
    pattern TEXT NOT NULL,
    usage_count INTEGER DEFAULT 0,
    lesson_name TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS har_entries (
    id INTEGER PRIMARY KEY,
    har_path TEXT NOT NULL,
    content_hash TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS shell_logs (
    id INTEGER PRIMARY KEY,
    log_path TEXT NOT NULL,
    content_hash TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL
);

