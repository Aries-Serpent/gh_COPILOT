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

import os
import sqlite3
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from utils.log_utils import _log_event

# Derive the default database path from the workspace to honor the
# database-first pattern in cross-platform environments.
DEFAULT_DB = Path(
    os.getenv("GH_COPILOT_WORKSPACE", Path.cwd())
) / "databases" / "learning_monitor.db"
TABLE = "enhanced_lessons_learned"


def ensure_lessons_table(db_path: Path = DEFAULT_DB) -> None:
    """Create the lessons table in ``db_path`` if missing.

    Parameters
    ----------
    db_path:
        Path to the SQLite database. If the file does not exist it will be
        created along with the ``enhanced_lessons_learned`` table.
    """

    with sqlite3.connect(db_path) as conn:
        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {TABLE} (
                description TEXT,
                source TEXT,
                timestamp TEXT,
                validation_status TEXT,
                tags TEXT
            )
            """
        )


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
    ensure_lessons_table(db_path)
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


def extract_lessons_from_codex_logs(db_path: Path) -> List[Dict[str, str]]:
    """Interpret Codex log patterns and convert them into lessons.

    This helper scans the ``codex_actions`` table produced by
    :mod:`utils.codex_log_db` and derives lessons from notable patterns in the
    log statements.  Currently, statements containing ``error``/``failed`` are
    tagged as ``error`` and those containing ``warning`` are tagged as
    ``warning``.  Only entries matching these patterns are returned.

    Parameters
    ----------
    db_path:
        Path to the Codex log SQLite database containing the
        ``codex_actions`` table.

    Returns
    -------
    list of dict
        Lessons in the format expected by :func:`store_lesson` with fields
        ``description``, ``source``, ``timestamp``, ``validation_status`` and
        ``tags``.
    """

    lessons: List[Dict[str, str]] = []
    if not db_path.exists():
        return lessons
    try:
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute(
                """
                SELECT statement, ts
                FROM codex_actions
                WHERE statement IS NOT NULL AND TRIM(statement) != ''
                """
            )
            seen: set[str] = set()
            for row in cur.fetchall():
                statement = row["statement"]
                lowered = statement.lower()
                tags: list[str] = []
                if "error" in lowered or "failed" in lowered:
                    tags.append("error")
                if "warning" in lowered:
                    tags.append("warning")
                if not tags or statement in seen:
                    continue
                seen.add(statement)
                lessons.append(
                    {
                        "description": statement,
                        "source": "codex_log",
                        "timestamp": row["ts"],
                        "validation_status": "pending",
                        "tags": ",".join(tags),
                    }
                )
    except sqlite3.Error as exc:  # pragma: no cover - log unexpected DB errors
        _log_event({"error": str(exc)}, table="lessons_learned_errors", db_path=db_path)
    return lessons


def store_lesson(
    description: str,
    source: str,
    timestamp: str,
    validation_status: str,
    *,
    tags: Optional[str] = None,
    db_path: Path = DEFAULT_DB,
) -> None:
    """Store a single lesson in the ``enhanced_lessons_learned`` table.

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
    >>> fetch_lessons_by_tag("documentation", db_path=Path("example.db"))
    [{'description': 'Document error handling',
      'source': 'docs',
      'timestamp': '2024-01-02T00:00:00Z',
      'validation_status': 'pending',
      'tags': 'documentation'}]
    """
    try:
        ensure_lessons_table(db_path)
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
    """Store multiple lessons using an ``executemany`` batch insert.

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
    ...     },
    ...     {
    ...         "description": "Prefer pathlib",
    ...         "source": "review",
    ...         "timestamp": "2024-01-04T00:00:00Z",
    ...         "validation_status": "pending",
    ...     },
    ... ]
    >>> store_lessons(lessons, db_path=Path("example.db"))
    >>> fetch_lessons_by_tag("style", db_path=Path("example.db"))
    [{'description': 'Use context managers',
      'source': 'review',
      'timestamp': '2024-01-03T00:00:00Z',
      'validation_status': 'validated',
      'tags': 'style'}]
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
        ensure_lessons_table(db_path)
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
    [{'description': 'Use context managers',
      'source': 'review',
      'timestamp': '2024-01-03T00:00:00Z',
      'validation_status': 'validated',
      'tags': 'style'}]
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
