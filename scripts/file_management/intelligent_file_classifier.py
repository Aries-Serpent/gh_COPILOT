"""Database-driven intelligent file classifier.

The classifier consults ``production.db`` to map file patterns to known
categories. It logs classification confidence for auditing purposes.
"""

from __future__ import annotations

import hashlib
import logging
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

__all__ = ["IntelligentFileClassifier"]


class IntelligentFileClassifier:
    """Classify files using ML/database patterns with duplicate detection."""

    def __init__(self, db_path: Path, verbose: bool | None = None) -> None:
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.logger = logging.getLogger(__name__)
        self.verbose = verbose or os.getenv("VERBOSE_LOGGING") == "1"
        if self.verbose:
            self.logger.setLevel(logging.DEBUG)
        self._init_tables()

    def _init_tables(self) -> None:
        """Ensure required tables exist."""
        with self.conn:
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS classification_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT NOT NULL,
                    file_hash TEXT NOT NULL,
                    category TEXT NOT NULL,
                    script_type TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    version INTEGER NOT NULL,
                    timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            self.conn.execute(
                "CREATE UNIQUE INDEX IF NOT EXISTS idx_classification_hash ON classification_results(file_hash)"
            )

    def _hash_file(self, path: Path) -> str:
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()

    def _query_patterns(self, suffix: str) -> list[tuple[str, str, int]]:
        cur = self.conn.execute(
            """
            SELECT functionality_category, script_type, COUNT(*) as frequency
            FROM enhanced_script_tracking
            WHERE script_path LIKE ?
            GROUP BY functionality_category, script_type
            ORDER BY frequency DESC
            """,
            (f"%{suffix}",),
        )
        return cur.fetchall()

    @staticmethod
    def calculate_classification_confidence(patterns: list[tuple[str, str, int]]) -> float:
        if not patterns:
            return 0.0
        total = sum(p[2] for p in patterns)
        return patterns[0][2] / total if total else 0.0

    def _is_duplicate(self, file_hash: str) -> bool:
        cur = self.conn.execute("SELECT 1 FROM script_tracking WHERE file_hash=?", (file_hash,))
        return cur.fetchone() is not None

    def _get_next_version(self, file_hash: str) -> int:
        cur = self.conn.execute(
            "SELECT version FROM classification_results WHERE file_hash=?",
            (file_hash,),
        )
        row = cur.fetchone()
        return (row[0] + 1) if row else 1

    def classify_file_autonomously(self, file_path: Path) -> Dict[str, Any]:
        """Classify files using database intelligence and ML patterns."""
        self.logger.debug("Classifying %s", file_path)
        file_hash = self._hash_file(file_path)
        patterns = self._query_patterns(file_path.suffix)

        category = patterns[0][0] if patterns else "general"
        script_type = patterns[0][1] if patterns else "utility"
        confidence = self.calculate_classification_confidence(patterns)

        duplicate = self._is_duplicate(file_hash)
        version = self._get_next_version(file_hash)

        with self.conn:
            if not duplicate:
                self.conn.execute(
                    "INSERT INTO script_tracking(file_path, file_hash, last_modified) VALUES (?, ?, ?)",
                    (str(file_path), file_hash, datetime.now().isoformat()),
                )
            self.conn.execute(
                "REPLACE INTO classification_results(file_path, file_hash, category,"
                " script_type, confidence, version, timestamp)"
                " VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)",
                (
                    str(file_path),
                    file_hash,
                    category,
                    script_type,
                    confidence,
                    version,
                ),
            )

        if self.verbose:
            self.logger.info(
                "[VERBOSE] %s -> %s/%s conf=%.2f dup=%s v%s",
                file_path,
                category,
                script_type,
                confidence,
                duplicate,
                version,
            )

        return {
            "category": category,
            "type": script_type,
            "confidence": confidence,
            "duplicate": duplicate,
            "version": version,
        }

    def classify(self, file_path: Path) -> str:
        """Return the classification category for the given file."""
        result = self.classify_file_autonomously(file_path)
        return result["category"]
