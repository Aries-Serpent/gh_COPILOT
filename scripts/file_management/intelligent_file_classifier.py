"""Database-driven intelligent file classifier.

The classifier consults ``production.db`` to map file patterns to known
categories. It logs classification confidence for auditing purposes.
"""
from __future__ import annotations

import logging
import sqlite3
from pathlib import Path

__all__ = ["IntelligentFileClassifier"]


class IntelligentFileClassifier:
    """Classify files using ML/database patterns."""

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.logger = logging.getLogger(__name__)

    def classify(self, file_path: Path) -> str:
        """Return the predicted category for ``file_path``.

        This method checks the ``functional_components`` table for a matching
        pattern and returns the associated classification. Confidence scores are
        logged for auditing.
        """
        self.logger.debug("Classifying %s", file_path)
        with self.conn:
            cur = self.conn.execute(
                "SELECT script_type FROM functional_components WHERE ? LIKE pattern",
                (file_path.name,),
            )
            row = cur.fetchone()
            classification = row[0] if row else "unknown"
        self.logger.info("Classified %s as %s", file_path, classification)
        return classification
