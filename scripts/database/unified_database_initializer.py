#!/usr/bin/env python3
"""Initialize the enterprise_assets.db database.
This script creates the unified schema used across all consolidation tools.
It performs integrity checks before writing to disk and includes visual
processing indicators and dual copilot validation hooks.
"""

from __future__ import annotations

import logging
import os
import sqlite3
from datetime import datetime
from pathlib import Path

from tqdm import tqdm

from utils.validation_utils import detect_zero_byte_files, validate_path
from utils.cross_platform_paths import CrossPlatformPathManager
from secondary_copilot_validator import SecondaryCopilotValidator

logger = logging.getLogger(__name__)

SIZE_LIMIT_MB = 99.9

TABLES: dict[str, str] = {
    "script_assets": (
        "CREATE TABLE IF NOT EXISTS script_assets ("
        "id INTEGER PRIMARY KEY,"
        "script_path TEXT NOT NULL,"
        "content_hash TEXT NOT NULL,"
        "created_at TEXT NOT NULL"
        ")"
    ),
    "documentation_assets": (
        "CREATE TABLE IF NOT EXISTS documentation_assets ("
        "id INTEGER PRIMARY KEY,"
        "doc_path TEXT NOT NULL,"
        "content_hash TEXT NOT NULL,"
        "created_at TEXT NOT NULL,"
        "modified_at TEXT NOT NULL"
        ")"
    ),
    "template_assets": (
        "CREATE TABLE IF NOT EXISTS template_assets ("
        "id INTEGER PRIMARY KEY,"
        "template_path TEXT NOT NULL,"
        "content_hash TEXT NOT NULL,"
        "created_at TEXT NOT NULL"
        ")"
    ),
    "pattern_assets": (
        "CREATE TABLE IF NOT EXISTS pattern_assets ("
        "id INTEGER PRIMARY KEY,"
        "pattern TEXT NOT NULL,"
        "usage_count INTEGER DEFAULT 0,"
        "created_at TEXT NOT NULL"
        ")"
    ),
    "enterprise_metadata": (
        "CREATE TABLE IF NOT EXISTS enterprise_metadata ("
        "id INTEGER PRIMARY KEY,"
        "key TEXT NOT NULL,"
        "value TEXT NOT NULL"
        ")"
    ),
    "integration_tracking": (
        "CREATE TABLE IF NOT EXISTS integration_tracking ("
        "id INTEGER PRIMARY KEY,"
        "integration_name TEXT NOT NULL,"
        "status TEXT NOT NULL,"
        "last_synced TEXT"
        ")"
    ),
    "cross_database_sync_operations": (
        "CREATE TABLE IF NOT EXISTS cross_database_sync_operations ("
        "id INTEGER PRIMARY KEY,"
        "operation TEXT NOT NULL,"
        "status TEXT NOT NULL,"
        "start_time TEXT NOT NULL,"
        "duration REAL NOT NULL,"
        "timestamp TEXT NOT NULL"
        ")"
    ),
}


def initialize_database(db_path: Path) -> None:
    """
    Create enterprise_assets.db with the expected schema.

    This function performs the following:
    - Validates the target path is within workspace and not inside backup.
    - Checks for zero-byte files in workspace before proceeding.
    - Aborts if the database file already exists and exceeds the size limit.
    - Logs start time, process ID, and uses a progress bar for table creation.
    - Implements timeout and ETC calculation.
    - Invokes secondary copilot validator for compliance.
    """
    start_time = datetime.now()
    process_id = os.getpid()
    logger.info("PROCESS STARTED: Initializing %s", db_path)
    logger.info("Start Time: %s", start_time.strftime('%Y-%m-%d %H:%M:%S'))
    logger.info("Process ID: %d", process_id)

    workspace_root = CrossPlatformPathManager.get_workspace_path()

    # Validate path is within workspace and not inside backup
    if not validate_path(db_path):
        logger.error("Invalid database path: %s", db_path)
        raise RuntimeError(f"Invalid database path: {db_path}")

    # Check for zero-byte files in workspace
    zero_bytes = detect_zero_byte_files(workspace_root)
    if zero_bytes:
        logger.error("Zero-byte files detected in workspace: %s", zero_bytes)
        raise RuntimeError(f"Zero-byte files detected: {zero_bytes}")

    # Check for size limit
    if db_path.exists() and db_path.stat().st_size > SIZE_LIMIT_MB * 1024 * 1024:
        logger.error("Existing database exceeds size limit %.1fMB", SIZE_LIMIT_MB)
        raise RuntimeError("Database file exceeds 99.9 MB")

    db_path.parent.mkdir(parents=True, exist_ok=True)
    timeout_minutes = 5
    timeout_seconds = timeout_minutes * 60
    elapsed = 0
    total_tables = len(TABLES)
    with sqlite3.connect(db_path, timeout=5) as conn, tqdm(
        total=total_tables, desc="Creating tables", unit="table",
        bar_format="{l_bar}{bar}| {n}/{total} [{elapsed}<{remaining}]"
    ) as bar:
        for idx, (table_name, sql) in enumerate(TABLES.items(), 1):
            conn.execute(sql)
            bar.set_description(f"Creating {table_name}")
            bar.update(1)
            elapsed = (datetime.now() - start_time).total_seconds()
            etc = ((elapsed / idx) * (total_tables - idx)) if idx > 0 else 0
            logger.info(
                "%s: Created | Progress: %d/%d | Elapsed: %.2fs | ETC: %.2fs",
                table_name, idx, total_tables, elapsed, etc
            )
            if elapsed > timeout_seconds:
                logger.error("Timeout exceeded during table creation")
                raise TimeoutError(f"Process exceeded {timeout_minutes} minute timeout")
        conn.commit()

    duration = (datetime.now() - start_time).total_seconds()
    logger.info("Database initialization complete in %.2fs", duration)

    # DUAL COPILOT PATTERN: Secondary validation
    validator = SecondaryCopilotValidator(logger)
    validation_passed = validator.validate_corrections([__file__])
    if validation_passed:
        logger.info("DUAL COPILOT VALIDATION: PASSED")
    else:
        logger.error("DUAL COPILOT VALIDATION: FAILED")


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    db_path = root / "databases" / "enterprise_assets.db"
    if db_path.exists():
        logger.info("%s already exists", db_path)
        return
    initialize_database(db_path)


if __name__ == "__main__":
    main()