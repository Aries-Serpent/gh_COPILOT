"""
Unified HAR ingestion module.

Features:
- Applies SQLite performance PRAGMAs.
- Ensures (and if needed, migrates) schema with columns:
    path, sha256, content_hash, created_at, metrics_json, metrics
- Maintains a UNIQUE index on (path, COALESCE(sha256, content_hash))
- Provides per-file ingestion with detailed event logging via IngestDAO if available.
- Computes SHA256 for duplicate detection; both sha256 and content_hash populated (content_hash kept for backward compatibility).
- Extracts lightweight metrics (count of entries, file size).
- Gracefully handles and counts errors; continues ingestion.
- Supports optional WAL checkpoint.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Optional

from tqdm import tqdm

# Optional DAO import for analytics / event logging
try:
    from .dao import IngestDAO  # type: ignore
except Exception:  # pragma: no cover
    IngestDAO = None  # type: ignore

PRAGMAS: tuple[str, ...] = (
    "PRAGMA journal_mode=WAL;",
    "PRAGMA synchronous=NORMAL;",
    "PRAGMA foreign_keys=ON;",
    "PRAGMA busy_timeout=10000;",
)

@dataclass
class IngestResult:
    inserted: int
    skipped: int
    errors: int
    duration_s: float
    checkpointed: bool

def _connect(db: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    for p in PRAGMAS:
        try:
            conn.execute(p)
        except Exception:
            pass
    return conn

def _ensure_schema(conn: sqlite3.Connection) -> None:
    """
    Create base table if not present, then add any missing columns for forward compatibility.
    """
    # Base table creation (minimal set; some columns may be absent in legacy DBs)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS har_entries (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          path TEXT NOT NULL,
          created_at TEXT NOT NULL
        );
        """
    )

    # Gather existing columns
    existing = {row[1] for row in conn.execute("PRAGMA table_info(har_entries)")}

    # Columns we want (nullable to allow additive migration)
    desired_columns: dict[str, str] = {
        "sha256": "ALTER TABLE har_entries ADD COLUMN sha256 TEXT",
        "content_hash": "ALTER TABLE har_entries ADD COLUMN content_hash TEXT",
        "metrics_json": "ALTER TABLE har_entries ADD COLUMN metrics_json TEXT",
        "metrics": "ALTER TABLE har_entries ADD COLUMN metrics TEXT",
    }

    for col, ddl in desired_columns.items():
        if col not in existing:
            try:
                conn.execute(ddl)
            except Exception:
                pass

    # Ensure UNIQUE index on path + hash
    try:
        conn.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS ux_har_entries_path_hash "
            "ON har_entries(path, COALESCE(sha256, content_hash))"
        )
    except Exception:
        pass

def _sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def _discover(inputs: list[Path]) -> list[Path]:
    files: list[Path] = []
    for base in inputs:
        if base.is_file() and base.suffix.lower() == ".har":
            files.append(base)
        elif base.is_dir():
            files.extend([p for p in base.rglob("*.har") if p.is_file()])
    # Deduplicate + stable ordering
    return sorted(set(files))

def _parse_metrics(p: Path) -> dict:
    size_bytes = p.stat().st_size
    try:
        obj = json.loads(p.read_text(encoding="utf-8", errors="ignore"))
        entries = obj.get("log", {}).get("entries", [])
        return {"entries": len(entries), "size_bytes": size_bytes}
    except Exception:
        return {"entries": None, "size_bytes": size_bytes}

def ingest_har_entries(
    db_path: str | Path,
    inputs: Iterable[str | Path],
    *,
    checkpoint: bool = False,
    dao: Optional['IngestDAO'] = None,  # type: ignore
    show_progress: bool = True,
) -> IngestResult:
    """
    Ingest provided HAR files (or directory trees) into the database.

    Parameters
    ----------
    db_path : Path | str
        Path to SQLite database.
    inputs : Iterable[str | Path]
        HAR files or directories containing HAR files.
    checkpoint : bool
        If True, attempt WAL checkpoint(TRUNCATE) after insert.
    dao : IngestDAO | None
        Optional explicit DAO (if not provided, instantiated if available).
    show_progress : bool
        Display a progress bar during ingestion.

    Returns
    -------
    IngestResult
    """
    start = time.perf_counter()
    db = Path(db_path)
    paths = [Path(p) for p in inputs]
    files = _discover(paths)

    inserted = 0
    errors = 0

    with _connect(db) as conn:
        _ensure_schema(conn)
        now = datetime.now(timezone.utc).isoformat()
        active_dao = dao or (IngestDAO(db) if IngestDAO else None)  # type: ignore

        # Preload existing hashes to optimize duplicate detection (optional)
        try:
            existing_hashes = {
                row[0]
                for row in conn.execute(
                    "SELECT COALESCE(sha256, content_hash) FROM har_entries"
                )
                if row[0] is not None
            }
        except Exception:
            existing_hashes = set()

        for f in tqdm(files, desc="HAR files", unit="file", disable=not show_progress):
            try:
                digest = _sha256_file(f)
                metrics = _parse_metrics(f)
                metrics_json = json.dumps(metrics)

                # Skip insertion attempt if already known (optimization)
                if digest in existing_hashes:
                    # Still log skip event
                    if active_dao:
                        try:
                            active_dao.log_event(
                                kind="har",
                                source=str(f),
                                target_table="har_entries",
                                target_pk=None,
                                status="skipped",
                                sha256=digest,
                                metrics=metrics,
                                connection=conn,
                            )
                        except Exception:
                            pass
                    continue

                with conn:  # atomic per row
                    conn.execute(
                        """
                        INSERT OR IGNORE INTO har_entries
                          (path, sha256, content_hash, created_at, metrics_json, metrics)
                        VALUES (?,?,?,?,?,?)
                        """,
                        (
                            str(f),
                            digest,
                            digest,  # populate both for backward compatibility
                            now,
                            metrics_json,
                            metrics_json,
                        ),
                    )
                    rowcount = conn.execute(
                        "SELECT changes()"
                    ).fetchone()[0]  # changes only for this connection

                    if rowcount > 0:
                        inserted += 1
                        existing_hashes.add(digest)
                        status = "ok"
                        rowid = conn.execute(
                            "SELECT id FROM har_entries WHERE path=? AND COALESCE(sha256, content_hash)=?",
                            (str(f), digest),
                        ).fetchone()[0]
                    else:
                        status = "skipped"
                        rowid = conn.execute(
                            "SELECT id FROM har_entries WHERE path=? AND COALESCE(sha256, content_hash)=?",
                            (str(f), digest),
                        ).fetchone()
                        rowid = rowid[0] if rowid else None

                if active_dao:
                    try:
                        active_dao.log_event(
                            kind="har",
                            source=str(f),
                            target_table="har_entries",
                            target_pk=rowid,
                            status=status,
                            sha256=digest,
                            metrics=metrics,
                            connection=conn,
                        )
                    except Exception:
                        pass

            except Exception as exc:
                errors += 1
                if active_dao:
                    try:
                        active_dao.log_event(
                            kind="har",
                            source=str(f),
                            target_table="har_entries",
                            target_pk=None,
                            status="error",
                            metrics={"error": str(exc)},
                            connection=conn,
                        )
                    except Exception:
                        pass

        if checkpoint:
            try:
                conn.execute("PRAGMA wal_checkpoint(TRUNCATE);")
            except Exception:
                pass

    duration = time.perf_counter() - start
    return IngestResult(
        inserted=inserted,
        skipped=len(files) - inserted,
        errors=errors,
        duration_s=duration,
        checkpointed=checkpoint,
    )

__all__ = ["ingest_har_entries", "IngestResult"]
if IngestDAO:  # type: ignore
    __all__.append("IngestDAO")
