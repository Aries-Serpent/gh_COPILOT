import sqlite3

from utils.lessons_learned_integrator import load_lessons

def test_load_lessons(tmp_path):
    db = tmp_path / "lessons.db"
    with sqlite3.connect(db) as conn:
        conn.execute(
            "CREATE TABLE enhanced_lessons_learned (description TEXT, tags TEXT)"
        )
        conn.execute(
            "INSERT INTO enhanced_lessons_learned (description, tags) VALUES (?, ?)",
            ("Use temp dirs", "testing"),
        )
    lessons = load_lessons(db)
    assert lessons == [{"description": "Use temp dirs", "tags": "testing"}]
