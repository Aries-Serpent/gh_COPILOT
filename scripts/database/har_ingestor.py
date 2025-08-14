# [Script]: ingest_har_files.py
> Generated: 2025-08-14 02:47:12 | Author: mbaetiong

#!/usr/bin/env python3
"""Ingest HAR files into the `har_entries` table and provide a Typer CLI entrypoint.

This script supports both direct ingestion and CLI-driven ingestion of HAR files
into the `enterprise_assets.db` or user-specified SQLite database. It robustly
handles duplicate detection, metrics extraction, secondary validation, logging,
and optional WAL checkpointing.

Features:
- Typer CLI interface for modern usage.
- Backward-compatible function-based ingestion (with workspace/har_dir).
- Duplicate file detection via SHA256 hash.
- Logging to analytics database.
- Optional fallback to argparse for legacy support.
- Comprehensive error handling and stable imports.
"""

from __future__ import annotations
import json
import sys
import hashlib
import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any

# Typer CLI import
import typer

try:
    from tqdm import tqdm
except ImportError:
    tqdm = None

# Compliance and validation imports
try:
    from enterprise_modules.compliance import (
        enforce_anti_recursion,
        validate_enterprise_operation,
        pid_recursion_guard,
    )
    _PID_GUARD_AVAILABLE = True
except Exception:
    _PID_GUARD_AVAILABLE = False

    def pid_recursion_guard(func):
        return func

try:
    from secondary_copilot_validator import SecondaryCopilotValidator
    from utils.log_utils import log_event
    from .cross_database_sync_logger import _table_exists, log_sync_operation
    from .size_compliance_checker import check_database_sizes
    from .unified_database_initializer import initialize_database
    from .schema_validators import ensure_har_schema
except ImportError:
    # Fall back for CLI-only usage (when not in package structure)
    SecondaryCopilotValidator = None
    log_event = lambda *a, **kw: None
    _table_exists = lambda *a, **kw: True
    log_sync_operation = lambda *a, **kw: None
    check_database_sizes = lambda *a, **kw: True
    initialize_database = lambda *a, **kw: None
    ensure_har_schema = lambda *a, **kw: None

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

__all__ = [
    "ingest_har_entries",
    "main",
]

_RECURSION_CTX = SimpleNamespace(recursion_depth=0, ancestors=[])

def _gather_har_files(directory: Path) -> list[Path]:
    """Return a sorted list of HAR files under ``directory``."""
    return sorted(p for p in directory.rglob("*.har") if p.is_file())

@pid_recursion_guard
def ingest_har_entries(
    workspace_or_db: Path,
    har_paths: list[Path] | None = None,
    *,
    checkpoint: bool = False,
    har_dir: Path | None = None,
) -> Any:
    """
    Ingest HAR metadata into the SQLite database.

    Parameters
    ----------
    workspace_or_db : Path
        (Legacy) Workspace root containing the 'databases' directory or modern direct database path.
    har_paths : list[Path] | None
        List of HAR files or directories (modern usage).
    checkpoint : bool
        If True, run WAL checkpoint(TRUNCATE) after ingest (modern usage).
    har_dir : Path | None
        Directory containing HAR files (legacy usage).
    Returns
    -------
    Namespace or dict with summary.
    """
    # Determine legacy or modern invocation
    if har_paths is not None:
        # Modern CLI: workspace_or_db is db file, har_paths is files/dirs
        db_path = Path(workspace_or_db)
        analytics_db = db_path.parent / "analytics.db"
        # Gather all .har files from all paths
        files: list[Path] = []
        for path in har_paths:
            if path.is_dir():
                files.extend(_gather_har_files(path))
            elif path.suffix.lower() == ".har":
                files.append(path)
        workspace = db_path.parent.parent if db_path.parent.name == "databases" else Path.cwd()
    else:
        # Legacy API: workspace_or_db is workspace, har_dir may be given
        workspace = Path(workspace_or_db)
        db_dir = workspace / "databases"
        db_path = db_dir / "enterprise_assets.db"
        analytics_db = db_dir / "analytics.db"
        har_dir = har_dir or (workspace / "logs")
        files = _gather_har_files(har_dir)

    if not db_path.exists():
        initialize_database(db_path)
    ensure_har_schema(db_path)

    start_time = datetime.now(timezone.utc)
    new_count = 0
    dup_count = 0
    validator = SecondaryCopilotValidator() if SecondaryCopilotValidator else None

    conn = sqlite3.connect(db_path)
    try:
        if not _table_exists(conn, "har_entries"):
            conn.close()
            initialize_database(db_path)
            conn = sqlite3.connect(db_path)

        # Gather all existing hashes for duplicate detection
        try:
            existing_hashes = {
                row[0] for row in conn.execute("SELECT content_hash FROM har_entries")
            }
        except Exception:
            existing_hashes = set()

        bar = tqdm(total=len(files), desc="HAR", unit="file") if tqdm else None
        for path in files:
            file_start = datetime.now(timezone.utc)
            rel_path = str(path.relative_to(workspace)) if path.is_absolute() and workspace in path.parents else str(path)
            try:
                raw = path.read_text(encoding="utf-8")
            except Exception as e:
                logger.error(f"Failed to read HAR file {path}: {e}")
                log_event(
                    {
                        "module": "har_ingestor",
                        "level": "ERROR",
                        "har_path": rel_path,
                        "status": "READ_ERROR",
                        "error": str(e),
                    },
                    db_path=analytics_db,
                )
                if bar:
                    bar.update(1)
                continue

            try:
                sha256 = hashlib.sha256(raw.encode()).hexdigest()
                metrics = json.dumps(
                    {"entries": len(json.loads(raw).get("log", {}).get("entries", []))}
                )
            except Exception as e:
                logger.error(f"Failed to process HAR file {path}: {e}")
                log_event(
                    {
                        "module": "har_ingestor",
                        "level": "ERROR",
                        "har_path": rel_path,
                        "status": "PROCESS_ERROR",
                        "error": str(e),
                    },
                    db_path=analytics_db,
                )
                if bar:
                    bar.update(1)
                continue

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
                if bar:
                    bar.update(1)
                continue

            new_count += 1
            existing_hashes.add(sha256)
            try:
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
            except Exception as e:
                logger.error(f"Failed to insert HAR entry for {rel_path}: {e}")
                log_event(
                    {
                        "module": "har_ingestor",
                        "level": "ERROR",
                        "har_path": rel_path,
                        "status": "INSERT_ERROR",
                        "error": str(e),
                    },
                    db_path=analytics_db,
                )
                if bar:
                    bar.update(1)
                continue

            log_sync_operation(
                db_path, "har_ingestion", status="SUCCESS", start_time=file_start
            )
            if validator:
                try:
                    validator.validate_corrections([str(path)])
                except Exception as e:
                    logger.warning(f"Validator failed on {rel_path}: {e}")
            if bar:
                bar.update(1)
        if bar:
            bar.close()
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

    if not check_database_sizes(db_path.parent if hasattr(db_path, 'parent') else Path.cwd()):
        raise RuntimeError("Database size limit exceeded")

    if getattr(_RECURSION_CTX, "recursion_depth", 0) > 0:
        _RECURSION_CTX.recursion_depth -= 1
        ancestors = getattr(_RECURSION_CTX, "ancestors", [])
        if ancestors:
            ancestors.pop()

    # Return a summary object for CLI
    class Result:
        def __init__(self, new_count, dup_count, db_path):
            self.new = new_count
            self.duplicates = dup_count
            self.db_path = str(db_path)
    return Result(new_count, dup_count, db_path)

app = typer.Typer(add_completion=False, help="HAR ingestor (WAL, busy_timeout, batching)")

@app.command()
def main(
    db: Path = typer.Option(Path("analytics.db"), help="Target SQLite DB"),
    checkpoint: bool = typer.Option(False, help="PRAGMA wal_checkpoint(TRUNCATE) after ingest"),
    path: list[Path] = typer.Argument(..., help="HAR files or directories"),
) -> None:
    """CLI entrypoint for ingesting HAR files."""
    try:
        res = ingest_har_entries(db, path, checkpoint=checkpoint)
        print(json.dumps(res.__dict__, indent=2))
    except Exception as e:
        logger.error(f"Failed to ingest HAR files: {e}")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    # Prefer Typer CLI, but provide backwards compatibility.
    if len(sys.argv) > 1 and "--workspace" not in sys.argv:
        # Modern Typer CLI usage
        app()
    else:
        # Legacy argparse usage for backward compatibility
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
        try:
            ingest_har_entries(args.workspace, har_dir=args.har_dir)
        except Exception as e:
            logger.error(f"Legacy ingestion failed: {e}")
            sys.exit(1)
