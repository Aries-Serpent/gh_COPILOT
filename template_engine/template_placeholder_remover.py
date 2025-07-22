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


def _fetch_template_ids(production_db: Path) -> List[tuple[int, str]]:
    if not production_db.exists():
        return []
    with sqlite3.connect(production_db) as conn:
        try:
            cur = conn.execute("SELECT id, template_content FROM code_templates")
            return [(row[0], row[1]) for row in cur.fetchall()]
        except sqlite3.Error:
            return []


def _log_removal(analytics_db: Path, template_id: int, removed: int) -> None:
    analytics_db.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(analytics_db) as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS placeholder_removal_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                template_id INTEGER,
                removed_count INTEGER,
                timestamp TEXT
            )"""
        )
        conn.execute(
            "INSERT INTO placeholder_removal_events (template_id, removed_count, timestamp) VALUES (?, ?, ?)",
            (template_id, removed, datetime.utcnow().isoformat()),
        )
        conn.commit()


def remove_placeholders(
    production_db: Path = DEFAULT_PRODUCTION_DB,
    analytics_db: Path = DEFAULT_ANALYTICS_DB,
) -> List[str]:
    templates = _fetch_template_ids(production_db)
    cleaned: List[str] = []
    with tqdm(templates, desc="Removing", unit="tmpl") as bar:
        for tid, content in bar:
            new_content, count = _PLACEHOLDER_RE.subn("", content)
            cleaned.append(new_content)
            _log_removal(analytics_db, tid, count)
    return cleaned


def validate_removals(analytics_db: Path = DEFAULT_ANALYTICS_DB) -> bool:
    if not analytics_db.exists():
        return False
    with sqlite3.connect(analytics_db) as conn:
        cur = conn.execute("SELECT COUNT(*) FROM placeholder_removal_events")
        return cur.fetchone()[0] > 0
