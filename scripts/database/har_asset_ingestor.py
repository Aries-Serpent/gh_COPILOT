#!/usr/bin/env python3
"""Ingest HAR files into enterprise_assets.db."""

from __future__ import annotations

import hashlib
import json
import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from tqdm import tqdm

from enterprise_modules.compliance import pid_recursion_guard, validate_enterprise_operation

from .cross_database_sync_logger import _table_exists, log_sync_operation
from .size_compliance_checker import check_database_sizes
from .unified_database_initializer import initialize_database
from scripts.validation.dual_copilot_orchestrator import DualCopilotOrchestrator
from utils.log_utils import log_event

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def _gather_har_files(directory: Path) -> list[Path]:
    """Return a sorted list of HAR files under ``directory``."""
    return sorted(p for p in directory.rglob("*.har") if p.is_file())


@pid_recursion_guard
def ingest_har_entries(workspace: Path, har_dir: Path | None = None) -> None:
    """Load HAR data into ``enterprise_assets.db``.

    Parameters
    ----------
    workspace:
        The workspace root containing the ``databases`` directory.
    har_dir:
        Optional path to the directory containing HAR files. Defaults to
        ``workspace / 'logs'``.
    """
    validate_enterprise_operation()
    db_dir = workspace / "databases"
    db_path = db_dir / "enterprise_assets.db"
    if not db_path.exists():
        initialize_database(db_path)

    har_dir = har_dir or (workspace / "logs")
    files = _gather_har_files(har_dir)

    start_time = datetime.now(timezone.utc)
    analytics_db = db_dir / "analytics.db"
    new_count = 0
    dup_count = 0

    conn = sqlite3.connect(db_path)
    try:
        if not _table_exists(conn, "har_entries"):
            conn.close()
            initialize_database(db_path)
            conn = sqlite3.connect(db_path)
        existing_hashes = {
            row[0] for row in conn.execute("SELECT content_hash FROM har_entries")
        }

        with conn, tqdm(total=len(files), desc="HAR", unit="file") as bar:
            for path in files:
                file_start = datetime.now(timezone.utc)
                rel_path = str(path.relative_to(workspace))
                content = path.read_text(encoding="utf-8")
                digest = hashlib.sha256(content.encode()).hexdigest()
                status = "DUPLICATE" if digest in existing_hashes else "SUCCESS"
                logger.info(
                    json.dumps(
                        {
                            "har_hash": digest,
                            "status": status,
                            "db_path": str(db_path),
                        }
                    )
                )
                if status == "DUPLICATE":
                    dup_count += 1
                    conn.commit()
                    log_sync_operation(
                        db_path,
                        "har_ingestion",
                        status="DUPLICATE",
                        start_time=file_start,
                    )
                    bar.update(1)
                    continue
                new_count += 1
                existing_hashes.add(digest)
                conn.execute(
                    (
                        "INSERT INTO har_entries (har_path, content_hash, created_at) VALUES (?, ?, ?)"
                    ),
                    (
                        rel_path,
                        digest,
                        datetime.now(timezone.utc).isoformat(),
                    ),
                )
                conn.commit()
                log_sync_operation(
                    db_path,
                    "har_ingestion",
                    status="SUCCESS",
                    start_time=file_start,
                )
                bar.update(1)
    finally:
        conn.commit()
        conn.close()

    log_sync_operation(db_path, "har_ingestion", start_time=start_time)
    summary = {
        "description": "har_ingestion_summary",
        "details": json.dumps(
            {
                "db_path": str(db_path),
                "new": new_count,
                "duplicates": dup_count,
            }
        ),
    }
    log_event(summary, db_path=analytics_db)
    logger.info(
        json.dumps(
            {"event": "har_ingestion_summary", **json.loads(summary["details"])}
        )
    )

    if not check_database_sizes(db_dir):
        raise RuntimeError("Database size limit exceeded")

    DualCopilotOrchestrator().validator.validate_corrections([str(db_path)])


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Ingest HAR files")
    parser.add_argument(
        "--workspace",
        default=Path(__file__).resolve().parents[1],
        type=Path,
        help="Workspace root",
    )
    parser.add_argument(
        "--har-dir",
        type=Path,
        help="Directory containing HAR files",
    )
    args = parser.parse_args()
    ingest_har_entries(args.workspace, args.har_dir)
