from __future__ import annotations

"""Utility helpers for asset ingestion scripts.

This module provides the :class:`AssetIngestor` which encapsulates common
logic used by the various ingestion scripts.  It handles file discovery,
content hashing, duplicate detection across multiple databases, and insertion
with optional version history.

Future ingestors (e.g. HAR, shell logs) should reuse this helper to avoid
code duplication and ensure consistent behaviour.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
from pathlib import Path
from typing import Iterable, List, Dict, Tuple, Callable, Any
import sqlite3

from scripts.database.cross_database_sync_logger import _table_exists
from scripts.database.unified_database_initializer import initialize_database

BUSY_TIMEOUT_MS = 30_000


@dataclass
class IngestorConfig:
    """Configuration for :class:`AssetIngestor`.

    Attributes
    ----------
    table:
        Name of the destination table inside ``enterprise_assets.db``.
    path_column:
        Column name storing the file path.
    patterns:
        Glob patterns used to discover files.
    """

    table: str
    path_column: str
    patterns: Iterable[str]


@dataclass
class IngestionResult:
    """Represents the outcome for a single file."""

    path: str
    status: str
    sha256: str
    md5: str


class AssetIngestor:
    """Generic helper for asset ingestion."""

    def __init__(self, workspace: Path, config: IngestorConfig) -> None:
        self.workspace = workspace
        self.config = config
        self.db_dir = workspace / "databases"
        self.db_path = self.db_dir / "enterprise_assets.db"
        if not self.db_path.exists():
            initialize_database(self.db_path)

    # ------------------------------------------------------------------
    def _discover(self, directory: Path) -> List[Path]:
        files: List[Path] = []
        for pattern in self.config.patterns:
            files.extend(p for p in directory.rglob(pattern) if p.is_file())
        # ensure stable ordering
        return sorted(set(files))

    def _hash_content(self, content: bytes) -> Tuple[str, str]:
        sha256 = hashlib.sha256(content).hexdigest()
        md5 = hashlib.md5(content).hexdigest()
        return sha256, md5

    # ------------------------------------------------------------------
    def ingest(
        self,
        directory: Path,
        *,
        dataset_dbs: Iterable[Path] | None = None,
        retain_history: bool = True,
        extra_columns: Dict[str, Callable[[Path], Any]] | None = None,
    ) -> List[IngestionResult]:
        """Ingest all files under ``directory``.

        Parameters
        ----------
        directory:
            Base directory containing candidate files.
        dataset_dbs:
            Optional additional databases whose content hashes should be
            considered for duplicate detection.
        retain_history:
            When ``True`` a new row with an incremented version is inserted
            whenever file content changes.  When ``False`` the existing row is
            updated in-place.
        extra_columns:
            Mapping of column name to a callable producing the value for a
            given path.  These columns are included in insert/update operations
            if provided.  Use this for fields such as ``modified_at``.
        """

        files = self._discover(directory)
        dataset_dbs = list(dataset_dbs or [])
        extra_columns = extra_columns or {}

        existing_paths: Dict[str, Tuple[str, int]] = {}
        existing_hashes: Dict[str, str] = {}

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute(f"PRAGMA busy_timeout={BUSY_TIMEOUT_MS};")
            if not _table_exists(conn, self.config.table):
                raise sqlite3.Error(f"table {self.config.table} not found")
            for row in conn.execute(
                f"SELECT {self.config.path_column}, content_hash, version FROM {self.config.table}"
            ):
                existing_paths[row[0]] = (row[1], row[2])
                existing_hashes[row[1]] = row[0]

        # Incorporate external datasets for duplicate detection
        for db in dataset_dbs:
            if not db.exists() or db == self.db_path:
                continue
            try:
                with sqlite3.connect(db) as ext_conn:
                    ext_conn.execute("PRAGMA journal_mode=WAL;")
                    ext_conn.execute(f"PRAGMA busy_timeout={BUSY_TIMEOUT_MS};")
                    if not _table_exists(ext_conn, self.config.table):
                        continue
                    for row in ext_conn.execute(
                        f"SELECT {self.config.path_column}, content_hash FROM {self.config.table}"
                    ):
                        existing_paths.setdefault(row[0], (row[1], 1))
                        existing_hashes.setdefault(row[1], row[0])
            except sqlite3.Error:
                # ignore secondary database errors
                continue

        results: List[IngestionResult] = []

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute(f"PRAGMA busy_timeout={BUSY_TIMEOUT_MS};")
            for path in files:
                rel_path = str(path.relative_to(self.workspace))
                content = path.read_bytes()
                digest, md5 = self._hash_content(content)
                extras = {col: fn(path) for col, fn in extra_columns.items()}
                if digest in existing_hashes:
                    results.append(IngestionResult(rel_path, "DUPLICATE", digest, md5))
                    continue
                if rel_path in existing_paths:
                    old_hash, version = existing_paths[rel_path]
                    if old_hash == digest:
                        results.append(IngestionResult(rel_path, "DUPLICATE", digest, md5))
                        continue
                    new_version = version + 1 if retain_history else version + 1
                    if retain_history:
                        cols = [self.config.path_column, "content_hash", "version", "created_at", *extras.keys()]
                        placeholders = ", ".join(["?"] * len(cols))
                        conn.execute(
                            f"INSERT INTO {self.config.table} ({', '.join(cols)}) VALUES ({placeholders})",
                            [
                                rel_path,
                                digest,
                                new_version,
                                datetime.now(timezone.utc).isoformat(),
                                *extras.values(),
                            ],
                        )
                    else:
                        set_clause = ", ".join(
                            ["content_hash=?", "version=?", "created_at=?", *[f"{c}=?" for c in extras.keys()]]
                        )
                        conn.execute(
                            f"UPDATE {self.config.table} SET {set_clause} WHERE {self.config.path_column}=?",
                            [
                                digest,
                                new_version,
                                datetime.now(timezone.utc).isoformat(),
                                *extras.values(),
                                rel_path,
                            ],
                        )
                    existing_paths[rel_path] = (digest, new_version)
                    existing_hashes[digest] = rel_path
                    results.append(IngestionResult(rel_path, "UPDATED", digest, md5))
                    continue
                # brand new file
                cols = [self.config.path_column, "content_hash", "version", "created_at", *extras.keys()]
                placeholders = ", ".join(["?"] * len(cols))
                conn.execute(
                    f"INSERT INTO {self.config.table} ({', '.join(cols)}) VALUES ({placeholders})",
                    [
                        rel_path,
                        digest,
                        1,
                        datetime.now(timezone.utc).isoformat(),
                        *extras.values(),
                    ],
                )
                existing_paths[rel_path] = (digest, 1)
                existing_hashes[digest] = rel_path
                results.append(IngestionResult(rel_path, "SUCCESS", digest, md5))
            conn.commit()

        return results
