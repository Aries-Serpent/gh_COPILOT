#!/usr/bin/env python3
"""Ingest templates and patterns into enterprise_assets.db."""

from __future__ import annotations

import hashlib
import logging
import sqlite3
from datetime import datetime
from pathlib import Path

from tqdm import tqdm

from .size_compliance_checker import check_database_sizes

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def _gather_template_files(directory: Path) -> list[Path]:
    """Return list of markdown files under directory."""
    return [p for p in directory.rglob("*.md") if p.is_file()]


def ingest_templates(workspace: Path, template_dir: Path | None = None) -> None:
    """Load template and pattern data into enterprise_assets.db."""
    db_dir = workspace / "databases"
    db_path = db_dir / "enterprise_assets.db"
    template_dir = template_dir or (workspace / "prompts")
    files = _gather_template_files(template_dir)

    with sqlite3.connect(db_path) as conn, tqdm(total=len(files), desc="Templates", unit="file") as bar:
        for path in files:
            content = path.read_text(encoding="utf-8")
            digest = hashlib.sha256(content.encode()).hexdigest()
            conn.execute(
                "INSERT INTO template_assets (template_path, content_hash, created_at) VALUES (?, ?, ?)",
                (str(path.relative_to(workspace)), digest, datetime.utcnow().isoformat()),
            )
            conn.execute(
                "INSERT INTO pattern_assets (pattern, usage_count, created_at) VALUES (?, 0, ?)",
                (content[:1000], datetime.utcnow().isoformat()),
            )
            bar.update(1)
        conn.commit()

    if not check_database_sizes(db_dir):
        raise RuntimeError("Database size limit exceeded")


if __name__ == "__main__":
    ROOT = Path(__file__).resolve().parents[1]
    ingest_templates(ROOT)
