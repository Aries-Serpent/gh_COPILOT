import os
import sqlite3
from pathlib import Path

os.environ["GH_COPILOT_DISABLE_VALIDATION"] = "1"

from template_engine.template_placeholder_remover import (
    remove_placeholders,
    validate_removals,
)


def test_remove_placeholders(tmp_path: Path) -> None:
    prod = tmp_path / "production.db"
    analytics = tmp_path / "analytics.db"
    with sqlite3.connect(prod) as conn:
        conn.execute(
            "CREATE TABLE code_templates (id INTEGER PRIMARY KEY, template_code TEXT)"
        )
        conn.execute(
            "INSERT INTO code_templates (template_code) VALUES ('def x(): {{PLACE}}')"
        )

    removed = remove_placeholders(prod, analytics)
    assert removed == 1

    with sqlite3.connect(prod) as conn:
        code = conn.execute("SELECT template_code FROM code_templates").fetchone()[0]
    assert "{{" not in code
    assert validate_removals(1, analytics)

