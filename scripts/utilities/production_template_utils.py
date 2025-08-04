"""Utilities for generating scripts from ``production.db``."""

from __future__ import annotations

import logging
import shutil
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
                "SELECT script_path FROM script_repository ORDER BY RANDOM() LIMIT 1"
            ).fetchone()
        if not row:
            logger.error("%s No scripts found in database", TEXT_INDICATORS["error"])
            return False

        src_file = workspace / row[0]
        if "scripts/quantum_placeholders" in src_file.as_posix():
            logger.error(
                "%s Placeholder modules are excluded from packaging",
                TEXT_INDICATORS["error"],
            )
            return False
        if not src_file.exists():
            logger.error("%s Missing script at %s", TEXT_INDICATORS["error"], src_file)
            return False

        output_file = output_dir / output_name
        shutil.copy(src_file, output_file)
        logger.info("%s Generated %s", TEXT_INDICATORS["success"], output_file)
        return True
    except Exception as exc:  # pragma: no cover - log and fail
        logger.error("%s Generation failed: %s", TEXT_INDICATORS["error"], exc)
        return False

