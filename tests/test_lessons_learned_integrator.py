import sqlite3
from pathlib import Path

from utils.lessons_learned_integrator import (
    load_lessons,
    store_lesson,
    store_lessons,
    fetch_lessons_by_tag,
)

def _create_table(db: Path) -> None:
    with sqlite3.connect(db) as conn:
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


def test_load_lessons(tmp_path):
    db = tmp_path / "lessons.db"
    _create_table(db)
    store_lesson(
        "Use temp dirs",
        source="tests",
        timestamp="2024-01-01",
        validation_status="validated",
        tags="testing",
        db_path=db,
    )
    lessons = load_lessons(db)
    assert lessons == [{"description": "Use temp dirs", "tags": "testing"}]


def test_store_lesson_and_fetch_by_tag(tmp_path):
    db = tmp_path / "lessons.db"
    _create_table(db)
    store_lesson(
        "Add more docs",
        source="review",
        timestamp="2024-01-02",
        validation_status="pending",
        tags="docs",
        db_path=db,
    )
    fetched = fetch_lessons_by_tag("docs", db_path=db)
    assert fetched[0]["description"] == "Add more docs"


def test_store_lessons_batch(tmp_path):
    db = tmp_path / "lessons.db"
    _create_table(db)
    lessons = [
        {
            "description": "Use context managers",
            "source": "review",
            "timestamp": "2024-01-03",
            "validation_status": "validated",
            "tags": "style",
        },
        {
            "description": "Avoid globals",
            "source": "review",
            "timestamp": "2024-01-04",
            "validation_status": "validated",
        },
    ]
    store_lessons(lessons, db_path=db)
    with sqlite3.connect(db) as conn:
        count = conn.execute(
            "SELECT COUNT(*) FROM enhanced_lessons_learned"
        ).fetchone()[0]
    assert count == 2
