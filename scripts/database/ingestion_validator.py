from __future__ import annotations

import hashlib
import sqlite3
from pathlib import Path

try:  # pragma: no cover - import guarded for optional dependency
    import numpy  # noqa: F401
    from template_engine.template_synchronizer import _compliance_score
    HAS_NUMPY = True
except ImportError:  # pragma: no cover - fallback when numpy is missing
    numpy = None  # type: ignore
    _compliance_score = None  # type: ignore
    HAS_NUMPY = False
from utils.log_utils import _log_event


class IngestionValidator:
    """Validate ingested asset hashes and compliance scores."""

    def __init__(self, workspace: Path, db_path: Path, analytics_db: Path) -> None:
        self.workspace = workspace
        self.db_path = db_path
        self.analytics_db = analytics_db

    def _fetch_logged_score(self, path: str) -> float | None:
        try:
            with sqlite3.connect(self.analytics_db) as conn:
                conn.execute(
                    "CREATE TABLE IF NOT EXISTS correction_logs (event TEXT, path TEXT, compliance_score REAL)"
                )
                row = conn.execute(
                    "SELECT compliance_score FROM correction_logs WHERE path=? ORDER BY rowid DESC LIMIT 1",
                    (path,),
                ).fetchone()
                return float(row[0]) if row else None
        except sqlite3.Error:
            return None

    def _validate_row(self, path: str, stored_hash: str, asset_type: str) -> bool:
        file_path = self.workspace / path
        if not file_path.exists():
            _log_event(
                {
                    "event": "ingestion_mismatch",
                    "asset_type": asset_type,
                    "path": path,
                    "reason": "missing",
                },
                table="correction_logs",
                db_path=self.analytics_db,
                test_mode=False,
            )
            return False
        content = file_path.read_text(encoding="utf-8")
        digest = hashlib.sha256(content.encode()).hexdigest()
        score = _compliance_score(content) if HAS_NUMPY and _compliance_score else None
        logged_score = self._fetch_logged_score(path)
        ok = digest == stored_hash and (
            not HAS_NUMPY or logged_score is None or logged_score == score
        )
        if not ok:
            _log_event(
                {
                    "event": "ingestion_mismatch",
                    "asset_type": asset_type,
                    "path": path,
                    "stored_hash": stored_hash,
                    "actual_hash": digest,
                    "stored_score": logged_score,
                    "actual_score": score,
                    "numpy_missing": not HAS_NUMPY,
                },
                table="correction_logs",
                db_path=self.analytics_db,
                test_mode=False,
            )
        return ok

    def validate(self) -> bool:
        try:
            with sqlite3.connect(self.db_path) as conn:
                docs = conn.execute("SELECT doc_path, content_hash FROM documentation_assets").fetchall()
                tmpls = conn.execute("SELECT template_path, content_hash FROM template_assets").fetchall()
        except sqlite3.Error:
            return False

        valid = True
        for path, digest in docs:
            if not self._validate_row(path, digest, "documentation"):
                valid = False
        for path, digest in tmpls:
            if not self._validate_row(path, digest, "template"):
                valid = False
        return valid


__all__ = ["IngestionValidator"]
