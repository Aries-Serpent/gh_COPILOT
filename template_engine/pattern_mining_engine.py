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
    """Mine templates in ``production_db`` and store discovered patterns.
    Results are also logged to ``analytics_db``.
    """
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
    # log to analytics
    analytics_db.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(analytics_db) as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS mined_pattern_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern TEXT,
                timestamp TEXT
            )"""
        )
        for pat in patterns:
            conn.execute(
                "INSERT INTO mined_pattern_log (pattern, timestamp) VALUES (?, ?)",
                (pat, datetime.utcnow().isoformat()),
            )
        conn.commit()
    return patterns


def validate_mining(analytics_db: Path, expected: int) -> bool:
    """Validate that at least ``expected`` patterns were logged."""
    if not analytics_db.exists():
        return False
    with sqlite3.connect(analytics_db) as conn:
        cur = conn.execute("SELECT COUNT(*) FROM mined_pattern_log")
        count = cur.fetchone()[0]
    return count >= expected
