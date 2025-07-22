"""Template placeholder removal utilities.

This module removes placeholders from templates stored in ``production.db`` and
logs each removal event to ``analytics.db``. Operations display progress using
``tqdm`` and a validation hook ensures that removal events were recorded.
"""

from __future__ import annotations

import re
import sqlite3
from datetime import datetime
from pathlib import Path

from tqdm import tqdm

DEFAULT_PRODUCTION_DB = Path("databases/production.db")
DEFAULT_ANALYTICS_DB = Path("databases/analytics.db")

PLACEHOLDER_RE = re.compile(r"{{\s*([A-Z0-9_]+)\s*}}")


def _log_removal(
    analytics_db: Path, template_id: int, placeholder: str
) -> None:
    analytics_db.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(analytics_db) as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS placeholder_removals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                template_id INTEGER,
                placeholder TEXT,
                timestamp TEXT
            )"""
        )
        insert_sql = (
            "INSERT INTO placeholder_removals ("
            "template_id, placeholder, timestamp"
            ") VALUES (?, ?, ?)"
        )
        conn.execute(
            insert_sql,
            (template_id, placeholder, datetime.utcnow().isoformat()),
        )
        conn.commit()


def remove_placeholders(
    production_db: Path = DEFAULT_PRODUCTION_DB,
    analytics_db: Path = DEFAULT_ANALYTICS_DB,
) -> int:
    """Remove placeholders from templates in ``production_db``."""
    if not production_db.exists():
        return 0

    removals = 0
    with sqlite3.connect(production_db) as conn:
        cur = conn.execute(
            "SELECT id, template_code FROM code_templates"
        )
        rows = cur.fetchall()

        with tqdm(total=len(rows), desc="Removing", unit="tmpl") as bar:
            for template_id, code in rows:
                matches = PLACEHOLDER_RE.findall(code)
                if matches:
                    new_code = PLACEHOLDER_RE.sub("", code)
                    conn.execute(
                        "UPDATE code_templates SET template_code=? WHERE id=?",
                        (new_code, template_id),
                    )
                    for ph in matches:
                        _log_removal(analytics_db, template_id, ph)
                        removals += 1
                bar.update(1)
        conn.commit()

    return removals


def validate_removals(
    expected: int, analytics_db: Path = DEFAULT_ANALYTICS_DB
) -> bool:
    """Validate at least ``expected`` removals were logged."""
    if not analytics_db.exists():
        return False
    with sqlite3.connect(analytics_db) as conn:
        cur = conn.execute("SELECT COUNT(*) FROM placeholder_removals")
        return cur.fetchone()[0] >= expected


__all__ = [
    "remove_placeholders",
    "validate_removals",
    "DEFAULT_PRODUCTION_DB",
    "DEFAULT_ANALYTICS_DB",
]
