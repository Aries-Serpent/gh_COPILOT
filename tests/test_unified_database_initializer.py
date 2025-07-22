import sqlite3
from pathlib import Path
import pytest

import os

from scripts.database.unified_database_initializer import initialize_database

# STUB TASK PROMPT: Write unit tests for unified_database_initializer.py.
# Test: All required tables are created.
# Test: Schema matches expected columns and types.
# Test: Initialization aborts if file exceeds 99.9 MB.
# Test: Visual processing indicators are logged.


def test_initializer_creates_tables(tmp_path: Path) -> None:
    os.environ["GH_COPILOT_WORKSPACE"] = str(tmp_path)
    os.environ["GH_COPILOT_BACKUP_ROOT"] = str(tmp_path / "backups")
    db_path = tmp_path / "enterprise_assets.db"
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


def test_initializer_aborts_large_file(tmp_path: Path) -> None:
    os.environ["GH_COPILOT_WORKSPACE"] = str(tmp_path)
    os.environ["GH_COPILOT_BACKUP_ROOT"] = str(tmp_path / "backups")
    db_path = tmp_path / "enterprise_assets.db"
    with open(db_path, "wb") as f:
        f.seek(100_000_000)
        f.write(b"0")

    with pytest.raises(RuntimeError):
        initialize_database(db_path)
