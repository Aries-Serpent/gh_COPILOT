import sqlite3
from pathlib import Path

from scripts.utilities.production_template_utils import generate_script_from_repository


def test_generate_script_from_repository(tmp_path: Path) -> None:
    db_dir = tmp_path / "databases"
    db_dir.mkdir()
    db_path = db_dir / "production.db"
    with sqlite3.connect(db_path) as conn:
        conn.execute("CREATE TABLE script_repository (script_content TEXT)")
        conn.execute("INSERT INTO script_repository VALUES ('print(\"hi\")')")

    result = generate_script_from_repository(tmp_path, "out.py")
    assert result is True
    assert (tmp_path / "generated_scripts" / "out.py").exists()
