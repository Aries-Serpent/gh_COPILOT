from __future__ import annotations

import re
import sqlite3
from datetime import datetime
from pathlib import Path

from tqdm import tqdm

DEFAULT_PRODUCTION_DB = Path("databases/production.db")
DEFAULT_ANALYTICS_DB = Path("databases/analytics.db")

_PLACEHOLDER_RE = re.compile(r"{{\s*([A-Z0-9_]+)\s*}}")


def _log_removal(analytics_db: Path, template_id: int, count: int) -> None:
    analytics_db.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(analytics_db) as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS placeholder_removals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                template_id INTEGER,
                removed_count INTEGER,
                timestamp TEXT
            )"""
        )
        conn.execute(
            "INSERT INTO placeholder_removals (template_id, removed_count, timestamp) VALUES (?, ?, ?)",
            (template_id, count, datetime.utcnow().isoformat()),
        )
        conn.commit()


def remove_placeholders(
    production_db: Path = DEFAULT_PRODUCTION_DB,
    analytics_db: Path = DEFAULT_ANALYTICS_DB,
) -> int:
    """Remove placeholders from templates and log removals."""
    removed_total = 0
    if not production_db.exists():
        return 0
    with sqlite3.connect(production_db) as conn:
        rows = conn.execute("SELECT id, template_code FROM code_templates").fetchall()
        with tqdm(total=len(rows), desc="Removing", unit="tmpl") as bar:
            for tid, code in rows:
                placeholders = _PLACEHOLDER_RE.findall(code or "")
                if placeholders:
                    new_code = _PLACEHOLDER_RE.sub("", code)
                    conn.execute(
                        "UPDATE code_templates SET template_code=? WHERE id=?",
                        (new_code, tid),
                    )
                    removed_total += len(placeholders)
                    _log_removal(analytics_db, tid, len(placeholders))
                bar.update(1)
        conn.commit()
    return removed_total


def validate_removals(analytics_db: Path, expected: int) -> bool:
    """Validate analytics records for placeholder removals."""
    if not analytics_db.exists():
        return False
    with sqlite3.connect(analytics_db) as conn:
        cur = conn.execute("SELECT SUM(removed_count) FROM placeholder_removals")
        count = cur.fetchone()[0]
    return (count or 0) >= expected
