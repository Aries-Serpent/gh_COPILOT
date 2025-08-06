from __future__ import annotations

import logging
import json
import re
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Mapping

from tqdm import tqdm
from utils.lessons_learned_integrator import load_lessons, apply_lessons

apply_lessons(logging.getLogger(__name__), load_lessons())

DEFAULT_PRODUCTION_DB = Path("databases/production.db")
DEFAULT_TEMPLATE_DOC_DB = Path("databases/template_documentation.db")
DEFAULT_ANALYTICS_DB = Path("databases/analytics.db")

_PLACEHOLDER_RE = re.compile(r"{{\s*([A-Z0-9_]+)\s*}}")


def find_placeholders(template_str: str) -> list[str]:
    """Return a list of placeholder names found in ``template_str``."""
    return _PLACEHOLDER_RE.findall(template_str)


def _load_placeholder_map(production_db: Path, template_doc_db: Path) -> dict[str, str]:
    mapping: dict[str, str] = {}
    if production_db.exists():
        with sqlite3.connect(production_db) as conn:
            for name, default in conn.execute("SELECT placeholder_name, default_value FROM template_placeholders"):
                clean = _PLACEHOLDER_RE.sub(r"\1", name) if _PLACEHOLDER_RE.search(name) else name.strip("{}")
                mapping[clean] = default
    # template_doc_db currently provides no values but may define placeholder names
    if template_doc_db.exists():
        with sqlite3.connect(template_doc_db) as conn:
            try:
                cur = conn.execute("SELECT placeholders FROM template_metadata")
            except sqlite3.Error:
                return mapping
            for row in cur.fetchall():
                try:
                    placeholders = json.loads(row[0]) if row[0] else []
                except json.JSONDecodeError:
                    placeholders = []
                for ph in placeholders:
                    mapping.setdefault(ph, "")
    return mapping


def _log_replacement(analytics_db: Path, placeholder: str, value: str) -> None:
    analytics_db.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(analytics_db) as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS placeholder_replacements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                placeholder TEXT,
                replacement TEXT,
                timestamp TEXT
            )"""
        )
        conn.execute(
            "INSERT INTO placeholder_replacements (placeholder, replacement, timestamp) VALUES (?, ?, ?)",
            (placeholder, value, datetime.utcnow().isoformat()),
        )
        conn.commit()


def replace_placeholders(
    template_str: str,
    db_paths: Mapping[str, Path] | None = None,
) -> str:
    """Replace placeholders in ``template_str`` using mappings from databases."""
    production_db = (db_paths or {}).get("production", DEFAULT_PRODUCTION_DB)
    template_doc_db = (db_paths or {}).get("template_doc", DEFAULT_TEMPLATE_DOC_DB)
    analytics_db = (db_paths or {}).get("analytics", DEFAULT_ANALYTICS_DB)

    mapping = _load_placeholder_map(production_db, template_doc_db)
    placeholders = find_placeholders(template_str)
    result = template_str

    with tqdm(total=len(placeholders), desc="Replacing", unit="ph") as bar:
        for ph in placeholders:
            value = mapping.get(ph)
            if value is not None:
                result = result.replace(f"{{{{{ph}}}}}", value)
                _log_replacement(analytics_db, ph, value)
            bar.update(1)
    return result
