import sqlite3
from pathlib import Path

from template_engine.template_placeholder_remover import (
    remove_placeholders,
    validate_removals,
)


def test_remove_placeholders(tmp_path: Path) -> None:
    prod = tmp_path / "production.db"
    with sqlite3.connect(prod) as conn:
        conn.execute(
            "CREATE TABLE code_templates (id INTEGER PRIMARY KEY, template_code TEXT)"
        )
        conn.execute(
            "INSERT INTO code_templates (id, template_code) VALUES (1, 'def foo(): {{PLACE}}')"
        )
    analytics = tmp_path / "analytics.db"
    removed = remove_placeholders(prod, analytics)
    assert removed > 0
    with sqlite3.connect(prod) as conn:
        code = conn.execute(
            "SELECT template_code FROM code_templates WHERE id=1"
        ).fetchone()[0]
    assert "{{" not in code
    assert validate_removals(analytics, removed)
