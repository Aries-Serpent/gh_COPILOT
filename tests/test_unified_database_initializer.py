import os
import sqlite3
from pathlib import Path

from scripts.database.unified_database_initializer import initialize_database


def test_initializer_creates_tables(tmp_path: Path) -> None:
    db_path = tmp_path / "enterprise_assets.db"
    os.environ["GH_COPILOT_WORKSPACE"] = str(tmp_path)
    initialize_database(db_path)
    with sqlite3.connect(db_path) as conn:
        tables = set(
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        )
    expected = {
        "script_assets",
        "documentation_assets",
        "template_assets",
        "pattern_assets",
        "enterprise_metadata",
        "integration_tracking",
        "cross_database_sync_operations",
    }
    assert expected.issubset(tables)


# STUB TASK PROMPT: Write additional unit tests for unified_database_initializer.py.
# Test: Schema columns and types match expected definitions.
# Test: Initialization aborts if database exceeds 99.9 MB.
# Test: Visual processing indicators (progress bar and start time logging) are emitted.
# Test: Dual copilot validation hook executes.
