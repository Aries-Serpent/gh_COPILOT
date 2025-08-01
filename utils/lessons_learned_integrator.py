"""Utilities for integrating lessons learned into runtime systems."""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import List, Dict

from utils.log_utils import _log_event

DEFAULT_DB = Path("databases/learning_monitor.db")
TABLE = "enhanced_lessons_learned"


def load_lessons(db_path: Path = DEFAULT_DB) -> List[Dict[str, str]]:
    """Load lessons from the lessons learned table.

    Parameters
    ----------
    db_path:
        Path to the SQLite database containing lessons.

    Returns
    -------
    list of dict
        Each dict contains the lesson ``description`` and optional ``tags``.
    """
    lessons: List[Dict[str, str]] = []
    if not db_path.exists():
        return lessons
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        try:
            cur.execute(
                f"SELECT description, COALESCE(tags, '') AS tags FROM {TABLE}"
            )
            for row in cur.fetchall():
                lessons.append({"description": row["description"], "tags": row["tags"]})
        except sqlite3.Error as exc:  # pragma: no cover - table may be missing
            _log_event({"error": str(exc)}, table="lessons_learned_errors", db_path=db_path)
    return lessons


def apply_lessons(logger, lessons: List[Dict[str, str]]) -> None:
    """Apply loaded lessons by logging them for transparency."""
    for lesson in lessons:
        logger.info("[INFO] Lesson applied: %s | tags=%s", lesson["description"], lesson["tags"])
