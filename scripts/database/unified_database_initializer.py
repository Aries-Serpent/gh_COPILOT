#!/usr/bin/env python3
"""
UnifiedDatabaseInitializer - Enterprise Utility Script
Generated: 2025-07-22 09:07:43 | Author: mbaetiong

Enterprise Standards Compliance:
- Flake8/PEP 8 Compliant
- Emoji-free code (text-based indicators only)
- Visual processing indicators
"""

from __future__ import annotations

import logging
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from tqdm import tqdm

from secondary_copilot_validator import SecondaryCopilotValidator
from utils.cross_platform_paths import CrossPlatformPathManager
from utils.logging_utils import setup_enterprise_logging
from utils.validation_utils import anti_recursion_guard, detect_zero_byte_files, validate_path

from .cross_database_sync_logger import log_sync_operation

# Database paths
PRODUCTION_DB = CrossPlatformPathManager.get_workspace_path() / "databases" / "production.db"

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
        "content_hash TEXT NOT NULL UNIQUE,"
        "version INTEGER NOT NULL DEFAULT 1,"
        "created_at TEXT NOT NULL,"
        "modified_at TEXT NOT NULL"
        ")"
    ),
    "template_assets": (
        "CREATE TABLE IF NOT EXISTS template_assets ("
        "id INTEGER PRIMARY KEY,"
        "template_path TEXT NOT NULL,"
        "content_hash TEXT NOT NULL UNIQUE,"
        "version INTEGER NOT NULL DEFAULT 1,"
        "created_at TEXT NOT NULL"
        ")"
    ),
    "pattern_assets": (
        "CREATE TABLE IF NOT EXISTS pattern_assets ("
        "id INTEGER PRIMARY KEY,"
        "pattern TEXT NOT NULL,"
        "usage_count INTEGER DEFAULT 0,"
        "lesson_name TEXT,"
        "created_at TEXT NOT NULL"
        ")"
    ),
    "har_entries": (
        "CREATE TABLE IF NOT EXISTS har_entries ("
        "id INTEGER PRIMARY KEY,"
        "path TEXT NOT NULL,"
        "content_hash TEXT NOT NULL UNIQUE,"
        "created_at TEXT NOT NULL,"
        "metrics TEXT"
        ")"
    ),
    "shell_logs": (
        "CREATE TABLE IF NOT EXISTS shell_logs ("
        "id INTEGER PRIMARY KEY,"
        "log_path TEXT NOT NULL,"
        "content_hash TEXT NOT NULL UNIQUE,"
        "created_at TEXT NOT NULL"
        ")"
    ),
    "enterprise_metadata": (
        "CREATE TABLE IF NOT EXISTS enterprise_metadata (id INTEGER PRIMARY KEY,key TEXT NOT NULL,value TEXT NOT NULL)"
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


def load_schema_from_production(tables: dict[str, str]) -> dict[str, str]:
    """Load CREATE TABLE statements from production.db if available."""
    if not PRODUCTION_DB.exists():
        return tables

    schema: dict[str, str] = {}
    with sqlite3.connect(PRODUCTION_DB) as conn:
        for name in tables:
            row = conn.execute(
                "SELECT sql FROM sqlite_master WHERE type='table' AND name=?",
                (name,),
            ).fetchone()
            if row and row[0]:
                schema[name] = row[0]

    # merge production schema with defaults
    return {**tables, **schema}


def _load_production_schema(prod_db: Path) -> None:
    """Log schema information from ``production.db`` if available."""
    if not prod_db.exists():
        logger.warning("production.db not found at %s", prod_db)
        return
    with sqlite3.connect(prod_db) as conn:
        tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        logger.info("Existing production tables: %s", [t[0] for t in tables])


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
    logger.info("Start Time: %s", start_time.strftime("%Y-%m-%d %H:%M:%S"))
    logger.info("Process ID: %d", process_id)

    prod_db = CrossPlatformPathManager.get_workspace_path() / "databases" / "production.db"
    _load_production_schema(prod_db)

    workspace_root = CrossPlatformPathManager.get_workspace_path()

    # Validate path is within workspace and not inside backup
    if os.getenv("GH_COPILOT_DISABLE_VALIDATION") != "1":
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
    tables = load_schema_from_production(TABLES)
    total_tables = len(tables)
    start_log = datetime.now(timezone.utc)
    with sqlite3.connect(db_path, timeout=5) as conn, tqdm(
        total=total_tables,
        desc="Creating tables",
        unit="table",
        bar_format="{l_bar}{bar}| {n}/{total} [{elapsed}<{remaining}]",
    ) as bar:
        for idx, (table_name, sql) in enumerate(tables.items(), 1):
            conn.execute(sql)
            bar.set_description(f"Creating {table_name}")
            bar.update(1)
            elapsed = (datetime.now() - start_time).total_seconds()
            etc = ((elapsed / idx) * (total_tables - idx)) if idx > 0 else 0
            logger.info(
                "%s: Created | Progress: %d/%d | Elapsed: %.2fs | ETC: %.2fs",
                table_name,
                idx,
                total_tables,
                elapsed,
                etc,
            )
            if elapsed > timeout_seconds:
                logger.error("Timeout exceeded during table creation")
                raise TimeoutError(f"Process exceeded {timeout_minutes} minute timeout")
        conn.commit()

    log_sync_operation(db_path, "init_start", start_time=start_log)

    # Post creation size check
    if db_path.stat().st_size > SIZE_LIMIT_MB * 1024 * 1024:
        raise RuntimeError("Database file exceeds 99.9 MB after initialization")

    duration = (datetime.now() - start_time).total_seconds()
    logger.info("Database initialization complete in %.2fs", duration)
    log_sync_operation(db_path, "init_complete", start_time=start_log)

    # DUAL COPILOT PATTERN: Secondary validation
    validator = SecondaryCopilotValidator(logger)
    validation_passed = validator.validate_corrections([__file__])
    if validation_passed:
        logger.info("DUAL COPILOT VALIDATION: PASSED")
    else:
        logger.error("DUAL COPILOT VALIDATION: FAILED")


@anti_recursion_guard
def main() -> None:
    root = Path(__file__).resolve().parents[1]
    db_path = root / "databases" / "enterprise_assets.db"
    if db_path.exists():
        logger.info("%s already exists", db_path)
        return
    initialize_database(db_path)


if __name__ == "__main__":
    setup_enterprise_logging()
    main()
