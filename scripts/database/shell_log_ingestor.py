#!/usr/bin/env python3
"""Ingest shell log files into enterprise_assets.db."""

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


def _gather_logs(directory: Path) -> list[Path]:
    """Return a sorted list of ``*.log`` files under ``directory``."""
    return sorted(p for p in directory.rglob("*.log") if p.is_file())


@pid_recursion_guard
def ingest_shell_logs(workspace: Path, logs_dir: Path | None = None) -> None:
    """Load shell log files into ``enterprise_assets.db``.

    Parameters
    ----------
    workspace:
        The workspace root containing the ``databases`` directory.
    logs_dir:
        Optional directory containing log files. Defaults to ``workspace / 'logs'``.
    """
    validate_enterprise_operation()
    db_dir = workspace / "databases"
    db_path = db_dir / "enterprise_assets.db"
    if not db_path.exists():
        initialize_database(db_path)

    logs_dir = logs_dir or (workspace / "logs")
    files = _gather_logs(logs_dir)

    start_time = datetime.now(timezone.utc)
    analytics_db = db_dir / "analytics.db"
    new_count = 0
    dup_count = 0

    conn = sqlite3.connect(db_path)
    try:
        if not _table_exists(conn, "shell_logs"):
            conn.close()
            initialize_database(db_path)
            conn = sqlite3.connect(db_path)
        existing_hashes = {
            row[0] for row in conn.execute("SELECT content_hash FROM shell_logs")
        }

        with conn, tqdm(total=len(files), desc="Logs", unit="file") as bar:
            for path in files:
                file_start = datetime.now(timezone.utc)
                rel_path = str(path.relative_to(workspace))
                content = path.read_text(encoding="utf-8")
                digest = hashlib.sha256(content.encode()).hexdigest()
                status = "DUPLICATE" if digest in existing_hashes else "SUCCESS"
                logger.info(
                    json.dumps(
                        {
                            "log_hash": digest,
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
                        "shell_log_ingestion",
                        status="DUPLICATE",
                        start_time=file_start,
                    )
                    bar.update(1)
                    continue
                new_count += 1
                existing_hashes.add(digest)
                conn.execute(
                    (
                        "INSERT INTO shell_logs (log_path, content_hash, created_at) VALUES (?, ?, ?)"
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
                    "shell_log_ingestion",
                    status="SUCCESS",
                    start_time=file_start,
                )
                bar.update(1)
    finally:
        conn.commit()
        conn.close()

    log_sync_operation(db_path, "shell_log_ingestion", start_time=start_time)
    summary = {
        "description": "shell_log_ingestion_summary",
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
            {"event": "shell_log_ingestion_summary", **json.loads(summary["details"])}
        )
    )

    if not check_database_sizes(db_dir):
        raise RuntimeError("Database size limit exceeded")

    DualCopilotOrchestrator().validator.validate_corrections([str(db_path)])


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Ingest shell log files")
    parser.add_argument(
        "--workspace",
        default=Path(__file__).resolve().parents[1],
        type=Path,
        help="Workspace root",
    )
    parser.add_argument(
        "--logs-dir",
        type=Path,
        help="Directory containing log files",
    )
    args = parser.parse_args()
    ingest_shell_logs(args.workspace, args.logs_dir)
