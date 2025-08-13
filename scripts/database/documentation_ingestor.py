#!/usr/bin/env python3
"""Ingest Markdown files into ``documentation_assets`` table.

The ingestor maintains a version history for each ``doc_path``. When a file
with an existing path is ingested and its content has changed, a new row is
inserted with an incremented ``version`` rather than skipping the file.
"""

from __future__ import annotations

import hashlib
import logging
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from tqdm import tqdm

from types import SimpleNamespace

from enterprise_modules.compliance import (
    enforce_anti_recursion,
    validate_enterprise_operation,
)

# pid_recursion_guard is optional during certain lightweight test runs where the
# full compliance module may not be available.  Expose a no-op fallback so the
# module can still be imported without errors.
try:  # pragma: no cover - optional import for environments without full compliance module
    from enterprise_modules.compliance import pid_recursion_guard  # type: ignore
    _PID_GUARD_AVAILABLE = True
except Exception:  # pragma: no cover - fallback to no-op decorator
    _PID_GUARD_AVAILABLE = False

    def pid_recursion_guard(func):
        return func
from template_engine.learning_templates import get_dataset_sources

from secondary_copilot_validator import SecondaryCopilotValidator
from utils.log_utils import log_event

from .cross_database_sync_logger import _table_exists, log_sync_operation
from .size_compliance_checker import check_database_sizes
from .unified_database_initializer import initialize_database

# Re-export the guard flag so tests can determine availability.
__all__ = ["ingest_documentation", "pid_recursion_guard", "_PID_GUARD_AVAILABLE"]

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

_RECURSION_CTX = SimpleNamespace()

BUSY_TIMEOUT_MS = 30_000


def _gather_markdown_files(directory: Path) -> list[Path]:
    """Return a sorted list of Markdown files under ``directory``."""
    files = [p for p in directory.rglob("*.md") if p.is_file()]
    return sorted(files)


@pid_recursion_guard
def ingest_documentation(
    workspace: Path,
    docs_dir: Path | None = None,
    timeout_seconds: int | None = None,
) -> None:
    """Ingest Markdown files into ``enterprise_assets.db``.

    Parameters
    ----------
    workspace:
        The workspace root containing the ``databases`` directory.
    docs_dir:
        Optional path to the documentation directory. Defaults to
        ``workspace / 'documentation'``.
    """
    enforce_anti_recursion(_RECURSION_CTX)
    validate_enterprise_operation()

    validator = SecondaryCopilotValidator()

    db_dir = workspace / "databases"
    db_path = db_dir / "enterprise_assets.db"
    analytics_db = Path(os.getenv("ANALYTICS_DB", str(db_dir / "analytics.db")))
    analytics_db.parent.mkdir(parents=True, exist_ok=True)

    if not db_path.exists():
        initialize_database(db_path)

    docs_dir = docs_dir or (workspace / "documentation")
    files = _gather_markdown_files(docs_dir)

    dataset_dbs = get_dataset_sources(str(workspace))
    existing_docs: set[str] = set()
    existing_sha256: set[str] = set()
    existing_md5: set[str] = set()

    if db_path.exists():
        try:
            with sqlite3.connect(db_path) as conn:
                conn.execute("PRAGMA journal_mode=WAL;")
                conn.execute(f"PRAGMA busy_timeout={BUSY_TIMEOUT_MS};")
                if _table_exists(conn, "documentation_assets"):
                    columns = {row[1] for row in conn.execute("PRAGMA table_info(documentation_assets)")}
                    if "version" not in columns:
                        conn.execute(
                            "ALTER TABLE documentation_assets ADD COLUMN version INTEGER NOT NULL DEFAULT 1"
                        )
                    existing_docs.update(
                        row[0]
                        for row in conn.execute(
                            "SELECT doc_path FROM documentation_assets"
                        )
                    )
                    existing_sha256.update(
                        row[0]
                        for row in conn.execute(
                            "SELECT content_hash FROM documentation_assets"
                        )
                    )
        except sqlite3.Error:
            existing_docs = set()
            existing_sha256 = set()

    primary_db = dataset_dbs[0] if dataset_dbs else None
    if primary_db and primary_db.exists() and primary_db != db_path:
        try:
            with sqlite3.connect(primary_db) as prod_conn:
                prod_conn.execute("PRAGMA journal_mode=WAL;")
                prod_conn.execute(f"PRAGMA busy_timeout={BUSY_TIMEOUT_MS};")
                if _table_exists(prod_conn, "documentation_assets"):
                    columns = {
                        row[1]
                        for row in prod_conn.execute("PRAGMA table_info(documentation_assets)")
                    }
                    if "version" not in columns:
                        prod_conn.execute(
                            "ALTER TABLE documentation_assets ADD COLUMN version INTEGER NOT NULL DEFAULT 1"
                        )
                    existing_docs.update(
                        row[0]
                        for row in prod_conn.execute(
                            "SELECT doc_path FROM documentation_assets"
                        )
                    )
                    existing_sha256.update(
                        row[0]
                        for row in prod_conn.execute(
                            "SELECT content_hash FROM documentation_assets"
                        )
                    )
        except sqlite3.Error:
            pass

    for doc_path in existing_docs:
        full_path = workspace / doc_path
        if full_path.exists():
            try:
                content = full_path.read_text(encoding="utf-8")
            except OSError:
                continue
            existing_md5.add(hashlib.md5(content.encode()).hexdigest())

    start_time = datetime.now(timezone.utc)
    logger.info("Starting documentation ingestion at %s", start_time.isoformat())

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute(f"PRAGMA busy_timeout={BUSY_TIMEOUT_MS};")
    try:
        if not _table_exists(conn, "documentation_assets"):
            conn.close()
            initialize_database(db_path)
            conn = sqlite3.connect(db_path)
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute(f"PRAGMA busy_timeout={BUSY_TIMEOUT_MS};")
        existing_sha256.update(
            row[0]
            for row in conn.execute(
                "SELECT content_hash FROM documentation_assets"
            )
        )

        with conn, tqdm(total=len(files), desc="Docs", unit="file") as bar:
            for path in files:
                file_start = datetime.now(timezone.utc)
                if timeout_seconds and (datetime.now(timezone.utc) - start_time).total_seconds() > timeout_seconds:
                    logger.error("Ingestion timed out")
                    raise TimeoutError("Documentation ingestion timed out")

                rel_path = str(path.relative_to(workspace))
                status = "SUCCESS"
                digest_sha256 = ""
                digest_md5 = ""

                if path.stat().st_size == 0:
                    status = "SKIPPED"
                    logger.warning("Skipping zero-byte file: %s", path)
                    conn.commit()
                    log_sync_operation(
                        db_path,
                        "documentation_ingestion",
                        status=status,
                        start_time=file_start,
                    )
                    log_event(
                        {
                            "module": "documentation_ingestor",
                            "level": "INFO",
                            "doc_path": rel_path,
                            "status": status,
                        },
                        db_path=analytics_db,
                    )
                    bar.update(1)
                    continue

                content = path.read_text(encoding="utf-8")
                digest_sha256 = hashlib.sha256(content.encode()).hexdigest()
                digest_md5 = hashlib.md5(content.encode()).hexdigest()

                existing = conn.execute(
                    (
                        "SELECT content_hash, version FROM documentation_assets "
                        "WHERE doc_path=? ORDER BY version DESC LIMIT 1"
                    ),
                    (rel_path,),
                ).fetchone()

                modified_at = datetime.fromtimestamp(
                    path.stat().st_mtime, timezone.utc
                ).isoformat()

                if existing:
                    if existing[0] == digest_sha256:
                        status = "UNCHANGED"
                    else:
                        status = "UPDATED"
                        new_version = existing[1] + 1
                        conn.execute(
                            (
                                "INSERT INTO documentation_assets "
                                "(doc_path, content_hash, version, created_at, modified_at) "
                                "VALUES (?, ?, ?, ?, ?)"
                            ),
                            (
                                rel_path,
                                digest_sha256,
                                new_version,
                                datetime.now(timezone.utc).isoformat(),
                                modified_at,
                            ),
                        )
                        existing_sha256.discard(existing[0])
                        existing_sha256.add(digest_sha256)
                    existing_md5.add(digest_md5)
                    existing_docs.add(rel_path)
                    conn.commit()
                    log_sync_operation(
                        db_path,
                        "documentation_ingestion",
                        status=status,
                        start_time=file_start,
                    )
                    log_event(
                        {
                            "module": "documentation_ingestor",
                            "level": "INFO",
                            "doc_path": rel_path,
                            "status": status,
                            "sha256": digest_sha256,
                            "md5": digest_md5,
                        },
                        db_path=analytics_db,
                    )
                    bar.update(1)
                    continue

                if digest_sha256 in existing_sha256 or digest_md5 in existing_md5:
                    status = "DUPLICATE"
                    logger.info(
                        "Duplicate content detected: %s (sha256=%s md5=%s)",
                        path,
                        digest_sha256,
                        digest_md5,
                    )
                    conn.commit()
                    log_sync_operation(
                        db_path,
                        "documentation_ingestion",
                        status=status,
                        start_time=file_start,
                    )
                    log_event(
                        {
                            "module": "documentation_ingestor",
                            "level": "INFO",
                            "doc_path": rel_path,
                            "status": status,
                            "sha256": digest_sha256,
                            "md5": digest_md5,
                        },
                        db_path=analytics_db,
                    )
                    bar.update(1)
                    continue

                status = "SUCCESS"
                conn.execute(
                    (
                        "INSERT INTO documentation_assets "
                        "(doc_path, content_hash, version, created_at, modified_at) "
                        "VALUES (?, ?, 1, ?, ?)"
                    ),
                    (
                        rel_path,
                        digest_sha256,
                        datetime.now(timezone.utc).isoformat(),
                        modified_at,
                    ),
                )
                conn.commit()
                log_sync_operation(
                    db_path,
                    "documentation_ingestion",
                    status=status,
                    start_time=file_start,
                )
                validator.validate_corrections([str(path)])
                log_event(
                    {
                        "module": "documentation_ingestor",
                        "level": "INFO",
                        "doc_path": rel_path,
                        "status": status,
                        "sha256": digest_sha256,
                        "md5": digest_md5,
                    },
                    db_path=analytics_db,
                )
                bar.update(1)
                existing_docs.add(rel_path)
                existing_sha256.add(digest_sha256)
                existing_md5.add(digest_md5)
    finally:
        conn.commit()
        conn.close()

    log_sync_operation(db_path, "documentation_ingestion", start_time=start_time)

    if not check_database_sizes(db_dir):
        raise RuntimeError("Database size limit exceeded")

    if getattr(_RECURSION_CTX, "recursion_depth", 0) > 0:
        _RECURSION_CTX.recursion_depth -= 1
        ancestors = getattr(_RECURSION_CTX, "ancestors", [])
        if ancestors:
            ancestors.pop()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Ingest documentation")
    parser.add_argument(
        "--workspace",
        default=Path(__file__).resolve().parents[1],
        type=Path,
        help="Workspace root",
    )
    parser.add_argument(
        "--docs-dir",
        type=Path,
        help="Directory containing markdown files",
    )

    args = parser.parse_args()
    ingest_documentation(args.workspace, args.docs_dir)
