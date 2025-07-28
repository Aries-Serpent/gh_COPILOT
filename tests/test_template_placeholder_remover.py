import os
import sqlite3
from datetime import datetime
from pathlib import Path

from template_engine.template_placeholder_remover import (
    remove_unused_placeholders,
    validate_removals,
)


def test_remove_unused_placeholders(tmp_path: Path) -> None:
    os.environ["GH_COPILOT_WORKSPACE"] = str(tmp_path)
    # Start time logging for visual processing indicator
    start_time = datetime.now()
    print("PROCESS STARTED: test_remove_unused_placeholders")
    print(f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Process ID: {os.getpid()}")

    # Setup test databases
    prod = tmp_path / "production.db"
    analytics = tmp_path / "analytics.db"
    with sqlite3.connect(prod) as conn:
        conn.execute(
            "CREATE TABLE code_templates (id INTEGER PRIMARY KEY, template_code TEXT)"
        )
        conn.execute(
            "CREATE TABLE template_placeholders (placeholder_name TEXT)"
        )
        conn.execute(
            "INSERT INTO code_templates (id, template_code) VALUES (1, 'def foo(): {{PLACE}}')"
        )
        conn.execute(
            "INSERT INTO template_placeholders (placeholder_name) VALUES ('VALID_PLACEHOLDER')"
        )

    # Remove unused placeholders from template string
    with sqlite3.connect(prod) as conn:
        code = conn.execute(
            "SELECT template_code FROM code_templates WHERE id=1"
        ).fetchone()[0]
    result = remove_unused_placeholders(code, prod, analytics, timeout_minutes=1)
    assert "{{" not in result, "Placeholder not removed from template"

    # Validate DUAL COPILOT pattern: check analytics for removal records
    assert validate_removals(1, analytics), "DUAL COPILOT validation failed"

    # Completion summary
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    print(f"TEST COMPLETED: test_remove_unused_placeholders in {duration:.2f}s")
    