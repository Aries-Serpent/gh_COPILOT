import sqlite3
from pathlib import Path

from session_db_tools import record_lesson


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


def test_record_lesson_success(tmp_path):
    db = tmp_path / "lessons.db"
    _create_table(db)
    result = record_lesson(
        db,
        "Ensure backups",
        source="tests",
        timestamp="2024-01-01",
        validation_status="validated",
        tags="testing",
    )
    assert result is True
    with sqlite3.connect(db) as conn:
        row = conn.execute(
            "SELECT description, source, timestamp, validation_status, tags FROM enhanced_lessons_learned"
        ).fetchone()
    assert row == (
        "Ensure backups",
        "tests",
        "2024-01-01",
        "validated",
        "testing",
    )


def test_record_lesson_failure(tmp_path):
    db = tmp_path / "lessons.db"
    # Table is not created to trigger failure
    result = record_lesson(
        db,
        "Missing table",
        source="tests",
        timestamp="2024-01-01",
        validation_status="validated",
        tags="testing",
    )
    assert result is False
