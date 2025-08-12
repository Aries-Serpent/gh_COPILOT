#!/usr/bin/env python3
"""Merge analytics databases into a single schema.

This script consolidates the smaller analytics-related databases into
``analytics.db``. Tables are copied into the target database. When a table
exists in both source and target but has a different schema, the data is copied
into a new table named ``<source>_<table>``.
"""

from __future__ import annotations

import logging
import sqlite3
from pathlib import Path
from time import perf_counter
from typing import Iterable

from ghc_monitoring.performance_tracker import benchmark_queries
from db_tools.database_first_utils import ensure_db_reference
from enterprise_modules.compliance import validate_enterprise_operation
from scripts.validation.secondary_copilot_validator import SecondaryCopilotValidator

logger = logging.getLogger(__name__)

ANALYTICS_SOURCES = [
    "advanced_analytics.db",
    "monitoring.db",
    "optimization_metrics.db",
    "performance_analysis.db",
    "performance_monitoring.db",
]


def _table_sql(conn: sqlite3.Connection, table: str) -> str:
    cur = conn.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (table,))
    row = cur.fetchone()
    return row[0] if row else ""


def _schemas_match(src: sqlite3.Connection, dest: sqlite3.Connection, table: str) -> bool:
    return _table_sql(src, table) == _table_sql(dest, table)


def _copy_table(src: sqlite3.Connection, dest: sqlite3.Connection, table: str, dest_name: str) -> None:
    create_sql = _table_sql(src, table)
    if dest_name != table:
        create_sql = create_sql.replace(f"CREATE TABLE {table}", f"CREATE TABLE {dest_name}")
    if not _table_sql(dest, dest_name):
        dest.execute(create_sql)
    columns = [row[1] for row in src.execute(f"PRAGMA table_info({table})")]
    placeholder = ",".join(["?"] * len(columns))
    rows = list(src.execute(f"SELECT {', '.join(columns)} FROM {table}"))
    if rows:
        dest.executemany(
            f"INSERT OR IGNORE INTO {dest_name} ({', '.join(columns)}) VALUES ({placeholder})",
            rows,
        )


def consolidate_databases(target: Path, sources: Iterable[Path]) -> None:
    """Merge multiple SQLite databases into ``target``."""
    with sqlite3.connect(target) as dest:
        dest.execute("PRAGMA foreign_keys=OFF")
        for source in sources:
            with sqlite3.connect(source) as src:
                tables = [
                    row[0]
                    for row in src.execute(
                        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
                    )
                ]
                for table in tables:
                    dest_name = table
                    if _table_sql(dest, table):
                        if not _schemas_match(src, dest, table):
                            dest_name = f"{source.stem}_{table}"
                    _copy_table(src, dest, table, dest_name)
        dest.commit()


def run() -> None:
    workspace = Path("databases")
    target = workspace / "analytics.db"
    sources = [workspace / name for name in ANALYTICS_SOURCES]
    logger.info("PRIMARY VALIDATION: analytics consolidation")
    if not ensure_db_reference(str(target)) or not validate_enterprise_operation(str(target)):
        logger.error("[ERROR] Database-first validation failed")
        return
    benchmark_queries(["SELECT count(*) FROM sqlite_master"], db_path=target)
    start = perf_counter()
    consolidate_databases(target, sources)
    duration = (perf_counter() - start) * 1000
    benchmark_queries(["SELECT count(*) FROM sqlite_master"], db_path=target)
    validator = SecondaryCopilotValidator(logger)
    logger.info("SECONDARY VALIDATION: analytics consolidation")
    if validator.validate_corrections([str(target)]):
        logger.info("Consolidation completed in %.2f ms", duration)
    else:
        logger.error("Consolidation failed secondary validation")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    validate_enterprise_operation()
    run()
