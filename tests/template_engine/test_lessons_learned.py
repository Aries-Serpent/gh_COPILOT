import logging
import sqlite3
from pathlib import Path

from utils.lessons_learned_integrator import (
    store_lesson,
    load_lessons,
    fetch_lessons_by_tag,
    apply_lessons,
)


def _init_db(path: Path) -> Path:
    with sqlite3.connect(path) as conn:
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
    return path


def test_store_retrieve_apply(tmp_path, caplog):
    db = _init_db(tmp_path / "lessons.db")
    store_lesson(
        "use mock DB",
        source="unit",
        timestamp="2024-01-01T00:00:00Z",
        validation_status="validated",
        tags="testing",
        db_path=db,
    )
    lessons = fetch_lessons_by_tag("testing", db_path=db)
    assert lessons and lessons[0]["description"] == "use mock DB"
    all_lessons = load_lessons(db_path=db)
    with caplog.at_level(logging.INFO):
        apply_lessons(logging.getLogger("lesson"), all_lessons)
    assert any("Lesson applied" in r.getMessage() for r in caplog.records)
