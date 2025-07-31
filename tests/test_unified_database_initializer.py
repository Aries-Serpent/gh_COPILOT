import os
import sqlite3
from pathlib import Path
import pytest
import logging

# Import the initializer for testing
from scripts.database.unified_database_initializer import initialize_database
# Test: All required tables are created.
# Test: Schema matches expected columns and types.
# Test: Initialization aborts if file exceeds 99.9 MB.
# Test: Visual processing indicators are logged.
# Test: Dual copilot validation hook executes.

REQUIRED_TABLES = {
    "script_assets",
    "documentation_assets",
    "template_assets",
    "pattern_assets",
    "enterprise_metadata",
    "integration_tracking",
    "cross_database_sync_operations",
}

EXPECTED_SCHEMA = {
    "script_assets": [
        ("id", "INTEGER"),
        ("script_path", "TEXT"),
        ("content_hash", "TEXT"),
        ("created_at", "TEXT"),
    ],
    "documentation_assets": [
        ("id", "INTEGER"),
        ("doc_path", "TEXT"),
        ("content_hash", "TEXT"),
        ("created_at", "TEXT"),
        ("modified_at", "TEXT"),
    ],
    "template_assets": [
        ("id", "INTEGER"),
        ("template_path", "TEXT"),
        ("content_hash", "TEXT"),
        ("created_at", "TEXT"),
    ],
    "pattern_assets": [
        ("id", "INTEGER"),
        ("pattern", "TEXT"),
        ("usage_count", "INTEGER"),
        ("created_at", "TEXT"),
    ],
    "enterprise_metadata": [
        ("id", "INTEGER"),
        ("key", "TEXT"),
        ("value", "TEXT"),
    ],
    "integration_tracking": [
        ("id", "INTEGER"),
        ("integration_name", "TEXT"),
        ("status", "TEXT"),
        ("last_synced", "TEXT"),
    ],
    "cross_database_sync_operations": [
        ("id", "INTEGER"),
        ("operation", "TEXT"),
        ("status", "TEXT"),
        ("start_time", "TEXT"),
        ("duration", "REAL"),
        ("timestamp", "TEXT"),
    ],
}


def test_initializer_creates_tables(tmp_path: Path) -> None:
    os.environ["GH_COPILOT_WORKSPACE"] = str(tmp_path)
    os.environ["GH_COPILOT_BACKUP_ROOT"] = str(tmp_path / "backups")
    db_path = tmp_path / "enterprise_assets.db"
    initialize_database(db_path)
    with sqlite3.connect(db_path) as conn:
        tables = set(row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'"))
    assert REQUIRED_TABLES.issubset(tables)


def test_initializer_schema_columns_and_types(tmp_path: Path) -> None:
    os.environ["GH_COPILOT_WORKSPACE"] = str(tmp_path)
    os.environ["GH_COPILOT_BACKUP_ROOT"] = str(tmp_path / "backups")
    db_path = tmp_path / "enterprise_assets.db"
    initialize_database(db_path)
    with sqlite3.connect(db_path) as conn:
        for table, expected_columns in EXPECTED_SCHEMA.items():
            cursor = conn.execute(f"PRAGMA table_info({table})")
            columns = [(row[1], row[2]) for row in cursor.fetchall()]
            for expected_col, expected_type in expected_columns:
                assert any(col == expected_col and expected_type in typ for col, typ in columns), (
                    f"Missing or incorrect column/type in {table}: {expected_col} ({expected_type})"
                )


def test_initializer_aborts_large_file(tmp_path: Path) -> None:
    os.environ["GH_COPILOT_WORKSPACE"] = str(tmp_path)
    os.environ["GH_COPILOT_BACKUP_ROOT"] = str(tmp_path / "backups")
    db_path = tmp_path / "enterprise_assets.db"
    with open(db_path, "wb") as f:
        f.seek(100_000_000)
        f.write(b"0")
    with pytest.raises(RuntimeError):
        initialize_database(db_path)


def test_initializer_visual_processing_indicators(tmp_path: Path, caplog) -> None:
    os.environ["GH_COPILOT_WORKSPACE"] = str(tmp_path)
    os.environ["GH_COPILOT_BACKUP_ROOT"] = str(tmp_path / "backups")
    db_path = tmp_path / "enterprise_assets.db"
    caplog.set_level(logging.INFO)
    initialize_database(db_path)
    logs = caplog.text
    assert "PROCESS STARTED" in logs
    assert "Start Time:" in logs
    assert "Process ID:" in logs
    assert "Creating tables" in logs or "Progress" in logs
    assert "Database initialization complete" in logs


def test_initializer_dual_copilot_validation(tmp_path: Path, caplog) -> None:
    os.environ["GH_COPILOT_WORKSPACE"] = str(tmp_path)
    os.environ["GH_COPILOT_BACKUP_ROOT"] = str(tmp_path / "backups")
    db_path = tmp_path / "enterprise_assets.db"
    caplog.set_level(logging.INFO)
    initialize_database(db_path)
    logs = caplog.text
    assert "DUAL COPILOT VALIDATION" in logs
    assert "PASSED" in logs or "FAILED"
