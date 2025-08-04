import sqlite3
from pathlib import Path

from enterprise_modules.task_stubs import load_template


def _setup_db(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "CREATE TABLE template_repository (template_name TEXT PRIMARY KEY, template_content TEXT, template_category TEXT)"
        )
        conn.execute(
            "INSERT INTO template_repository (template_name, template_content, template_category) VALUES (?, ?, ?)",
            ("sample", "db version", "test"),
        )


def test_db_template_overrides_file(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    db_path = tmp_path / "databases" / "production.db"
    _setup_db(db_path)

    templates_dir = tmp_path / "templates"
    templates_dir.mkdir()
    (templates_dir / "sample.tpl").write_text("file version")

    content = load_template("sample", templates_dir=templates_dir)
    assert content == "db version"


def test_falls_back_to_file_when_db_missing(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    templates_dir = tmp_path / "templates"
    templates_dir.mkdir()
    (templates_dir / "sample.tpl").write_text("file version")

    content = load_template("sample", templates_dir=templates_dir)
    assert content == "file version"
