#!/usr/bin/env python3
"""Ingest HAR files into the ``har_entries`` table.

The ingestor scans a directory for ``.har`` files, computes a SHA256 hash
for each file, extracts simple metrics, and stores the results in the
``enterprise_assets.db`` database. Duplicate files are skipped based on
the content hash. All operations are logged to ``analytics.db``.
"""

from __future__ import annotations

import hashlib
import json
import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

from tqdm import tqdm

from enterprise_modules.compliance import (
    enforce_anti_recursion,
    validate_enterprise_operation,
)

try:  # pragma: no cover - optional guard
    from enterprise_modules.compliance import pid_recursion_guard  # type: ignore
    _PID_GUARD_AVAILABLE = True
except Exception:  # pragma: no cover - fallback to no-op
    _PID_GUARD_AVAILABLE = False

    def pid_recursion_guard(func):  # type: ignore
        return func

from secondary_copilot_validator import SecondaryCopilotValidator
from utils.log_utils import log_event

from .cross_database_sync_logger import _table_exists, log_sync_operation
from .size_compliance_checker import check_database_sizes
from .unified_database_initializer import initialize_database

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

_RECURSION_CTX = SimpleNamespace(recursion_depth=0, ancestors=[])


def _gather_har_files(directory: Path) -> list[Path]:
    """Return a sorted list of HAR files under ``directory``."""

    return sorted(p for p in directory.rglob("*.har") if p.is_file())


@pid_recursion_guard
def ingest_har_entries(workspace: Path, har_dir: Path | None = None) -> None:
    """Load HAR metadata into ``enterprise_assets.db``.

    Parameters
    ----------
    workspace:
        Workspace root containing the ``databases`` directory.
    har_dir:
        Optional directory containing HAR files. Defaults to ``workspace / 'logs'``.
    """

    validate_enterprise_operation()
    enforce_anti_recursion(_RECURSION_CTX)
    _RECURSION_CTX.recursion_depth += 1

    db_dir = workspace / "databases"
    db_path = db_dir / "enterprise_assets.db"
    analytics_db = db_dir / "analytics.db"

    if not db_path.exists():
        initialize_database(db_path)

    har_dir = har_dir or (workspace / "logs")
    files = _gather_har_files(har_dir)

    start_time = datetime.now(timezone.utc)
    new_count = 0
    dup_count = 0
    validator = SecondaryCopilotValidator()

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
                raw = path.read_text(encoding="utf-8")
                sha256 = hashlib.sha256(raw.encode()).hexdigest()
                metrics = json.dumps(
                    {"entries": len(json.loads(raw).get("log", {}).get("entries", []))}
                )

                status = "DUPLICATE" if sha256 in existing_hashes else "SUCCESS"

                log_event(
                    {
                        "module": "har_ingestor",
                        "level": "INFO",
                        "har_path": rel_path,
                        "status": status,
                        "sha256": sha256,
                    },
                    db_path=analytics_db,
                )

                if status == "DUPLICATE":
                    dup_count += 1
                    log_sync_operation(
                        db_path, "har_ingestion", status="DUPLICATE", start_time=file_start
                    )
                    bar.update(1)
                    continue

                new_count += 1
                existing_hashes.add(sha256)
                conn.execute(
                    (
                        "INSERT INTO har_entries (path, content_hash, created_at, metrics) "
                        "VALUES (?, ?, ?, ?)"
                    ),
                    (
                        rel_path,
                        sha256,
                        datetime.now(timezone.utc).isoformat(),
                        metrics,
                    ),
                )
                log_sync_operation(
                    db_path, "har_ingestion", status="SUCCESS", start_time=file_start
                )
                validator.validate_corrections([str(path)])
                bar.update(1)
    finally:
        conn.commit()
        conn.close()

    log_sync_operation(db_path, "har_ingestion", start_time=start_time)

    log_event(
        {
            "module": "har_ingestor",
            "level": "INFO",
            "description": "har_ingestion_summary",
            "details": json.dumps(
                {"db_path": str(db_path), "new": new_count, "duplicates": dup_count}
            ),
        },
        db_path=analytics_db,
    )

    if not check_database_sizes(db_dir):
        raise RuntimeError("Database size limit exceeded")

    if getattr(_RECURSION_CTX, "recursion_depth", 0) > 0:
        _RECURSION_CTX.recursion_depth -= 1
        ancestors = getattr(_RECURSION_CTX, "ancestors", [])
        if ancestors:
            ancestors.pop()


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
