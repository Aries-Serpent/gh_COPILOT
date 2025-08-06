import sqlite3
from pathlib import Path

from template_engine.placeholder_utils import replace_placeholders


def test_replace_placeholders_ignores_unknown(tmp_path: Path) -> None:
    prod = tmp_path / "prod.db"
    tmpl = tmp_path / "tmpl.db"
    analytics = tmp_path / "analytics.db"

    with sqlite3.connect(prod) as conn:
        conn.execute(
            "CREATE TABLE template_placeholders (placeholder_name TEXT, default_value TEXT)"
        )
    sqlite3.connect(tmpl).close()

    result = replace_placeholders(
        "Hello {{UNKNOWN}}",
        {"production": prod, "template_doc": tmpl, "analytics": analytics},
    )

    assert result == "Hello {{UNKNOWN}}"
    assert not analytics.exists()
