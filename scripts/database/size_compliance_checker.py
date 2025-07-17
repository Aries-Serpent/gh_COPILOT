#!/usr/bin/env python3
"""Verify SQLite database sizes do not exceed 99.9 MB."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

from tqdm import tqdm

THRESHOLD_MB = 99.9

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def check_database_sizes(directory: Path, threshold_mb: float = THRESHOLD_MB) -> bool:
    """Return True if all database files are below the size threshold."""
    db_files = list(directory.glob("*.db"))
    compliant = True
    with tqdm(total=len(db_files), desc="Checking sizes", unit="db") as bar:
        for db_path in db_files:
            size_mb = db_path.stat().st_size / (1024 * 1024)
            if size_mb > threshold_mb:
                logger.error("%s exceeds %.1f MB (%.2f MB)", db_path, threshold_mb, size_mb)
                compliant = False
            bar.update(1)
    return compliant


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Check SQLite database sizes")
    parser.add_argument(
        "directory",
        nargs="?",
        default=Path(__file__).resolve().parents[1] / "databases",
        type=Path,
        help="Directory containing databases",
    )

    args = parser.parse_args()

    if not args.directory.exists():
        logger.error("Databases directory not found: %s", args.directory)
        sys.exit(1)
    if check_database_sizes(args.directory):
        logger.info("All databases comply with size restrictions")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
