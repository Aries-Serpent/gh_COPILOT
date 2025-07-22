from __future__ import annotations

import re
import sqlite3
from datetime import datetime
from pathlib import Path

from tqdm import tqdm

DEFAULT_PRODUCTION_DB = Path("databases/production.db")


def extract_patterns(templates: list[str]) -> list[str]:
    """Extract recurring 3-word patterns from templates."""
    patterns = set()
    for text in templates:
        words = re.findall(r"\w+", text)
        for i in range(len(words) - 2):
            patterns.add(" ".join(words[i : i + 3]))
    return list(patterns)


def mine_patterns(production_db: Path = DEFAULT_PRODUCTION_DB) -> list[str]:
    """Mine templates in ``production_db`` and store discovered patterns."""
    templates = []
    if production_db.exists():
        with sqlite3.connect(production_db) as conn:
            try:
                cur = conn.execute("SELECT template_code FROM code_templates")
                templates = [row[0] for row in cur.fetchall()]
            except sqlite3.Error:
                templates = []
    patterns = extract_patterns(templates)
    if production_db.exists():
        with sqlite3.connect(production_db) as conn:
            conn.execute(
                """CREATE TABLE IF NOT EXISTS mined_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern TEXT,
                    mined_at TEXT
                )"""
            )
            for pat in tqdm(patterns, desc="Storing", unit="pat"):
                conn.execute(
                    "INSERT INTO mined_patterns (pattern, mined_at) VALUES (?, ?)",
                    (pat, datetime.utcnow().isoformat()),
                )
            conn.commit()
    return patterns
