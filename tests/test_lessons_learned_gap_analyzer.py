import sqlite3
from pathlib import Path

from scripts.analysis.lessons_learned_gap_analyzer import LessonsLearnedGapAnalyzer
from template_engine.learning_templates import get_lesson_templates


def test_dataset_coverage_validation(tmp_path: Path, monkeypatch) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))
    monkeypatch.chdir(workspace)
    db_dir = workspace / "databases"
    db_dir.mkdir()
    prod_db = db_dir / "production.db"
    with sqlite3.connect(prod_db) as conn:
        conn.execute("CREATE TABLE lessons_learned (lesson_key TEXT)")
        for key in get_lesson_templates().keys():
            conn.execute("INSERT INTO lessons_learned VALUES (?)", (key,))
    analyzer = LessonsLearnedGapAnalyzer(str(workspace))
    assert analyzer.validate_dataset_coverage()
    # remove one lesson
    removed = next(iter(get_lesson_templates().keys()))
    with sqlite3.connect(prod_db) as conn:
        conn.execute("DELETE FROM lessons_learned WHERE lesson_key=?", (removed,))
    assert not analyzer.validate_dataset_coverage()


def test_append_lesson_cli(monkeypatch):
    from scripts.analysis import lessons_learned_gap_analyzer as lga

    captured = {}
    monkeypatch.setattr(lga, "store_lesson", lambda **kw: captured.update(kw))
    assert lga.main(["--lesson", "new gap lesson"]) == 0
    assert captured["description"] == "new gap lesson"
