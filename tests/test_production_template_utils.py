import sqlite3
from pathlib import Path

from scripts.utilities.production_template_utils import generate_script_from_repository


def test_generate_script_from_repository(tmp_path: Path) -> None:
    db_dir = tmp_path / "databases"
    db_dir.mkdir()
    db_path = db_dir / "production.db"
    with sqlite3.connect(db_path) as conn:
        conn.execute("CREATE TABLE script_repository (script_path TEXT)")
        conn.execute("INSERT INTO script_repository VALUES ('demo.py')")

    (tmp_path / "demo.py").write_text("print('hi')")

    result = generate_script_from_repository(tmp_path, "out.py")
    assert result is True
    assert (tmp_path / "generated_scripts" / "out.py").exists()


def test_generate_script_from_repository_missing_file(tmp_path: Path, caplog) -> None:
    db_dir = tmp_path / "databases"
    db_dir.mkdir()
    db_path = db_dir / "production.db"
    with sqlite3.connect(db_path) as conn:
        conn.execute("CREATE TABLE script_repository (script_path TEXT)")
        conn.execute("INSERT INTO script_repository VALUES ('demo.py')")

    with caplog.at_level("ERROR"):
        result = generate_script_from_repository(tmp_path, "out.py")

    assert result is False
    assert not (tmp_path / "generated_scripts" / "out.py").exists()
    assert any("Missing script" in rec.getMessage() for rec in caplog.records)


def test_generate_script_from_repository_empty_table(tmp_path: Path, caplog) -> None:
    db_dir = tmp_path / "databases"
    db_dir.mkdir()
    db_path = db_dir / "production.db"
    with sqlite3.connect(db_path) as conn:
        conn.execute("CREATE TABLE script_repository (script_path TEXT)")

    with caplog.at_level("ERROR"):
        result = generate_script_from_repository(tmp_path, "out.py")

    assert result is False
    assert not (tmp_path / "generated_scripts" / "out.py").exists()
    assert any("No scripts found" in rec.getMessage() for rec in caplog.records)
