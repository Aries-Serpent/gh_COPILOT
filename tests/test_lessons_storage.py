"""Tests for lesson storage utilities.

These tests verify that lessons can be stored and retrieved from a
temporary SQLite database. They cover single inserts, batch inserts and
filtering by tag.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from utils.lessons_learned_integrator import (
    fetch_lessons_by_tag,
    store_lesson,
    store_lessons,
)


def _create_table(db_path: Path) -> None:
    """Create the ``enhanced_lessons_learned`` table in ``db_path``."""
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE enhanced_lessons_learned (
                description TEXT,
                source TEXT,
                timestamp TEXT,
                validation_status TEXT,
                tags TEXT
            )
            """
        )


def test_store_lesson_inserts_row(tmp_path: Path) -> None:
    db = tmp_path / "lessons.db"
    _create_table(db)
    store_lesson(
        "Document edge cases",
        source="review",
        timestamp="2024-02-01",
        validation_status="validated",
        tags="docs",
        db_path=db,
    )
    with sqlite3.connect(db) as conn:
        row = conn.execute(
            "SELECT description, source, timestamp, validation_status, tags FROM enhanced_lessons_learned"
        ).fetchone()
    assert row == (
        "Document edge cases",
        "review",
        "2024-02-01",
        "validated",
        "docs",
    )


def test_store_lessons_batch_inserts_rows(tmp_path: Path) -> None:
    db = tmp_path / "lessons.db"
    _create_table(db)
    lessons = [
        {
            "description": "Use context managers",
            "source": "review",
            "timestamp": "2024-02-02",
            "validation_status": "validated",
            "tags": "style",
        },
        {
            "description": "Avoid globals",
            "source": "review",
            "timestamp": "2024-02-03",
            "validation_status": "validated",
        },
    ]
    store_lessons(lessons, db_path=db)
    with sqlite3.connect(db) as conn:
        count = conn.execute(
            "SELECT COUNT(*) FROM enhanced_lessons_learned"
        ).fetchone()[0]
    assert count == len(lessons)


def test_fetch_lessons_by_tag_filters(tmp_path: Path) -> None:
    db = tmp_path / "lessons.db"
    _create_table(db)
    store_lesson(
        "Tag filtering works",
        source="tests",
        timestamp="2024-02-04",
        validation_status="validated",
        tags="test",
        db_path=db,
    )
    store_lesson(
        "Different tag",
        source="tests",
        timestamp="2024-02-05",
        validation_status="validated",
        tags="other",
        db_path=db,
    )
    results = fetch_lessons_by_tag("test", db_path=db)
    assert len(results) == 1
    assert results[0]["tags"] == "test"
    assert results[0]["description"] == "Tag filtering works"

