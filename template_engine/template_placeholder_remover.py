from __future__ import annotations

import re
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List

from tqdm import tqdm

DEFAULT_PRODUCTION_DB = Path("databases/production.db")
DEFAULT_ANALYTICS_DB = Path("databases/analytics.db")
_PLACEHOLDER_RE = re.compile(r"{{\s*([A-Z0-9_]+)\s*}}")


def _load_valid_placeholders(db: Path) -> List[str]:
    names: List[str] = []
    if db.exists():
        with sqlite3.connect(db) as conn:
            try:
                cur = conn.execute("SELECT placeholder_name FROM template_placeholders")
                names = [row[0].strip('{}') for row in cur.fetchall()]
            except sqlite3.Error:
                names = []
    return names


def remove_unused_placeholders(
    template: str,
    production_db: Path = DEFAULT_PRODUCTION_DB,
    analytics_db: Path = DEFAULT_ANALYTICS_DB,
) -> str:
    """Remove placeholders not defined in production DB."""
    valid = set(_load_valid_placeholders(production_db))
    found = _PLACEHOLDER_RE.findall(template)
    result = template
    analytics_db.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(analytics_db) as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS placeholder_removals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                placeholder TEXT,
                ts TEXT
            )"""
        )
        with tqdm(total=len(found), desc="Removing", unit="ph") as bar:
            for ph in found:
                if ph not in valid:
                    pattern = r"{{\s*%s\s*}}" % re.escape(ph)
                    result = re.sub(pattern, "", result)
                    conn.execute(
                        "INSERT INTO placeholder_removals (placeholder, ts) VALUES (?, ?)",
                        (ph, datetime.utcnow().isoformat()),
                    )
                bar.update(1)
        conn.commit()
    return result


def validate_removals(expected_count: int, analytics_db: Path = DEFAULT_ANALYTICS_DB) -> bool:
    """DUAL COPILOT validation for placeholder removals."""
    with sqlite3.connect(analytics_db) as conn:
        cur = conn.execute("SELECT COUNT(*) FROM placeholder_removals")
        return cur.fetchone()[0] >= expected_count

__all__ = ["remove_unused_placeholders", "validate_removals"]
