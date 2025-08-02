import logging

from utils.lessons_learned_integrator import (
    apply_lessons,
    ensure_lessons_table,
    fetch_lessons_by_tag,
    load_lessons,
    store_lesson,
)


def test_store_retrieve_apply(tmp_path, caplog):
    db = tmp_path / "lessons.db"
    ensure_lessons_table(db)
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
