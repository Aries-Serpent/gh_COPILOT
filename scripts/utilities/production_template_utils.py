"""Utilities for generating scripts from ``production.db``."""

from __future__ import annotations

import logging
import sqlite3
from pathlib import Path


TEXT_INDICATORS = {
    "success": "[SUCCESS]",
    "error": "[ERROR]",
}

logger = logging.getLogger(__name__)


def generate_script_from_repository(workspace: Path, output_name: str) -> bool:
    """Fetch a random script from ``production.db`` and store it."""

    db_path = workspace / "databases" / "production.db"
    output_dir = workspace / "generated_scripts"
    output_dir.mkdir(parents=True, exist_ok=True)
    try:
        with sqlite3.connect(db_path) as conn:
            row = conn.execute(
                "SELECT script_content FROM script_repository ORDER BY RANDOM() LIMIT 1"
            ).fetchone()
        if not row:
            logger.error("%s No scripts found in database", TEXT_INDICATORS["error"])
            return False

        output_file = output_dir / output_name
        output_file.write_text(row[0])
        logger.info("%s Generated %s", TEXT_INDICATORS["success"], output_file)
        return True
    except Exception as exc:  # pragma: no cover - log and fail
        logger.error("%s Generation failed: %s", TEXT_INDICATORS["error"], exc)
        return False

