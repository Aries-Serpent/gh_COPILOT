#!/usr/bin/env python3
from __future__ import annotations
import sqlite3
from pathlib import Path

def seed(db: Path) -> None:
    con = sqlite3.connect(db)
    con.executescript(
        """
        CREATE TABLE IF NOT EXISTS documentation_templates(id TEXT PRIMARY KEY, path TEXT NOT NULL, content TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS script_templates(id TEXT PRIMARY KEY, path TEXT NOT NULL, content TEXT NOT NULL);
        INSERT OR IGNORE INTO documentation_templates(id, path, content) VALUES ('readme', 'README', '# Hello {{project}}');
        INSERT OR IGNORE INTO script_templates(id, path, content) VALUES ('hello', 'hello', "print('ok')");
        """
    )
    con.commit(); con.close()

if __name__ == "__main__":
    seed(Path("documentation.db"))
    print("seeded documentation.db with starter templates")
