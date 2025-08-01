"""Utilities for integrating lessons learned into runtime systems.

This module provides helpers for persisting and retrieving lessons in the
``enhanced_lessons_learned`` table.  The table stores each lesson's
``description``, ``source``, ``timestamp``, ``validation_status`` and optional
``tags``.

Examples
--------
>>> store_lesson(
...     "Prefer temp directories",
...     source="unit_test",
...     timestamp="2024-01-01T00:00:00Z",
...     validation_status="validated",
...     tags="testing",
...     db_path=Path("example.db"),
... )
>>> fetch_lessons_by_tag("testing", db_path=Path("example.db"))
[{'description': 'Prefer temp directories',
  'source': 'unit_test',
  'timestamp': '2024-01-01T00:00:00Z',
  'validation_status': 'validated',
  'tags': 'testing'}]
"""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import List, Dict, Iterable, Optional

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


def store_lesson(
    description: str,
    source: str,
    timestamp: str,
    validation_status: str,
    *,
    tags: Optional[str] = None,
    db_path: Path = DEFAULT_DB,
) -> None:
    """Store a single lesson in the lessons learned table.

    Parameters
    ----------
    description, source, timestamp, validation_status:
        Fields describing the lesson entry.
    tags:
        Optional comma-separated tags.
    db_path:
        Path to the SQLite database.

    Examples
    --------
    >>> store_lesson(
    ...     "Document error handling",
    ...     source="docs",
    ...     timestamp="2024-01-02T00:00:00Z",
    ...     validation_status="pending",
    ...     tags="documentation",
    ...     db_path=Path("example.db"),
    ... )
    """
    try:
        with sqlite3.connect(db_path) as conn:
            conn.execute(
                f"""
                INSERT INTO {TABLE}
                    (description, source, timestamp, validation_status, tags)
                VALUES (?, ?, ?, ?, ?)
                """,
                (description, source, timestamp, validation_status, tags),
            )
    except sqlite3.Error as exc:  # pragma: no cover - log unexpected DB errors
        _log_event({"error": str(exc)}, table="lessons_learned_errors", db_path=db_path)


def store_lessons(
    lessons: Iterable[Dict[str, str]],
    db_path: Path = DEFAULT_DB,
) -> None:
    """Store multiple lessons using a batch insert.

    Parameters
    ----------
    lessons:
        Iterable of lesson dictionaries containing ``description``, ``source``,
        ``timestamp``, ``validation_status`` and optional ``tags``.
    db_path:
        Path to the SQLite database.

    Examples
    --------
    >>> lessons = [
    ...     {
    ...         "description": "Use context managers",
    ...         "source": "review",
    ...         "timestamp": "2024-01-03T00:00:00Z",
    ...         "validation_status": "validated",
    ...         "tags": "style",
    ...     }
    ... ]
    >>> store_lessons(lessons, db_path=Path("example.db"))
    """
    records = [
        (
            lesson["description"],
            lesson["source"],
            lesson["timestamp"],
            lesson["validation_status"],
            lesson.get("tags"),
        )
        for lesson in lessons
    ]
    try:
        with sqlite3.connect(db_path) as conn:
            conn.executemany(
                f"""
                INSERT INTO {TABLE}
                    (description, source, timestamp, validation_status, tags)
                VALUES (?, ?, ?, ?, ?)
                """,
                records,
            )
    except sqlite3.Error as exc:  # pragma: no cover
        _log_event({"error": str(exc)}, table="lessons_learned_errors", db_path=db_path)


def fetch_lessons_by_tag(tag: str, db_path: Path = DEFAULT_DB) -> List[Dict[str, str]]:
    """Fetch lessons that contain a given tag.

    Parameters
    ----------
    tag:
        Tag to search for within the ``tags`` field.
    db_path:
        Path to the SQLite database.

    Returns
    -------
    list of dict
        Matching rows with all lesson fields.

    Examples
    --------
    >>> fetch_lessons_by_tag("style", db_path=Path("example.db"))
    []
    """
    results: List[Dict[str, str]] = []
    if not db_path.exists():
        return results
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        try:
            cur.execute(
                f"""
                SELECT description, source, timestamp, validation_status,
                       COALESCE(tags, '') AS tags
                FROM {TABLE}
                WHERE tags LIKE ?
                """,
                (f"%{tag}%",),
            )
            for row in cur.fetchall():
                results.append(
                    {
                        "description": row["description"],
                        "source": row["source"],
                        "timestamp": row["timestamp"],
                        "validation_status": row["validation_status"],
                        "tags": row["tags"],
                    }
                )
        except sqlite3.Error as exc:  # pragma: no cover
            _log_event({"error": str(exc)}, table="lessons_learned_errors", db_path=db_path)
    return results
