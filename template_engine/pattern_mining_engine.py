from __future__ import annotations

import re
import sqlite3
from datetime import datetime
from pathlib import Path

from tqdm import tqdm

DEFAULT_PRODUCTION_DB = Path("databases/production.db")
DEFAULT_ANALYTICS_DB = Path("databases/analytics.db")


def extract_patterns(templates: list[str]) -> list[str]:
    """Extract recurring 3-word patterns from templates."""
    patterns = set()
    for text in templates:
        words = re.findall(r"\w+", text)
        for i in range(len(words) - 2):
            patterns.add(" ".join(words[i : i + 3]))
    return list(patterns)


def mine_patterns(
    production_db: Path = DEFAULT_PRODUCTION_DB,
    analytics_db: Path = DEFAULT_ANALYTICS_DB,
) -> list[str]:
    """Mine templates and store discovered patterns with analytics logging."""
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

    if analytics_db.exists() or analytics_db.parent.exists():
        with sqlite3.connect(analytics_db) as conn:
            conn.execute(
                """CREATE TABLE IF NOT EXISTS pattern_mining_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern_count INTEGER,
                    timestamp TEXT
                )"""
            )
            conn.execute(
                "INSERT INTO pattern_mining_logs (pattern_count, timestamp) VALUES (?, ?)",
                (len(patterns), datetime.utcnow().isoformat()),
            )
            conn.commit()
    return patterns


def validate_mining(expected: int, analytics_db: Path = DEFAULT_ANALYTICS_DB) -> bool:
    """Validate that at least ``expected`` patterns were logged."""
    if not analytics_db.exists():
        return False
    with sqlite3.connect(analytics_db) as conn:
        cur = conn.execute("SELECT MAX(pattern_count) FROM pattern_mining_logs")
        row = cur.fetchone()
        return (row[0] or 0) >= expected


__all__ = [
    "extract_patterns",
    "mine_patterns",
    "validate_mining",
    "DEFAULT_PRODUCTION_DB",
    "DEFAULT_ANALYTICS_DB",
]
