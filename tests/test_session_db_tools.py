import sqlite3

from scripts.session.session_db_tools import record_lesson
from utils.lessons_learned_integrator import ensure_lessons_table


def test_record_lesson_success(tmp_path):
    db = tmp_path / "lessons.db"
    ensure_lessons_table(db)
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


def test_record_lesson_creates_table(tmp_path):
    db = tmp_path / "lessons.db"
    # Table not pre-created; store_lesson should create it automatically
    result = record_lesson(
        db,
        "Missing table",
        source="tests",
        timestamp="2024-01-01",
        validation_status="validated",
        tags="testing",
    )
    assert result is True
