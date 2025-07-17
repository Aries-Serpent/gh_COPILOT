#!/usr/bin/env python3
"""Ingest Markdown files into documentation_assets table."""

from __future__ import annotations

import hashlib
import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from tqdm import tqdm

from .size_compliance_checker import check_database_sizes

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def _gather_markdown_files(directory: Path) -> list[Path]:
    """Return a sorted list of Markdown files under ``directory``."""
    files = [p for p in directory.rglob("*.md") if p.is_file()]
    return sorted(files)


def ingest_documentation(workspace: Path, docs_dir: Path | None = None) -> None:
    """Ingest Markdown files into ``enterprise_assets.db``.

    Parameters
    ----------
    workspace:
        The workspace root containing the ``databases`` directory.
    docs_dir:
        Optional path to the documentation directory. Defaults to
        ``workspace / 'documentation'``.
    """
    db_dir = workspace / "databases"
    db_path = db_dir / "enterprise_assets.db"
    docs_dir = docs_dir or (workspace / "documentation")
    files = _gather_markdown_files(docs_dir)

    with sqlite3.connect(db_path) as conn, tqdm(total=len(files), desc="Docs", unit="file") as bar:
        for path in files:
            content = path.read_text(encoding="utf-8")
            digest = hashlib.sha256(content.encode()).hexdigest()
            conn.execute(
                (
                    "INSERT INTO documentation_assets "
                    "(doc_path, content_hash, created_at) VALUES (?, ?, ?)"
                ),
                (
                    str(path.relative_to(workspace)),
                    digest,
                    datetime.now(timezone.utc).isoformat(),
                ),
            )
            bar.update(1)
        conn.commit()

    if not check_database_sizes(db_dir):
        raise RuntimeError("Database size limit exceeded")


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
