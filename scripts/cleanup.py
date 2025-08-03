#!/usr/bin/env python3
"""Legacy asset cleanup based on template clusters."""
from __future__ import annotations

import argparse
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(message)s")


def cleanup_legacy_assets(cluster_file: Path, dry_run: bool = True) -> list[Path]:
    """Remove legacy assets referenced in cluster outputs.

    Parameters
    ----------
    cluster_file:
        Path to a JSON file produced by ``cluster_templates``.
    dry_run:
        If True, no files are deleted.

    Returns
    -------
    list[Path]
        List of removed file paths.
    """
    if not cluster_file.exists():
        logger.info("No cluster output found; nothing to clean")
        return []
    data = json.loads(cluster_file.read_text(encoding="utf-8"))
    legacy_paths = [Path(p) for p in data.get("0", [])]
    removed: list[Path] = []
    cutoff = datetime.now() - timedelta(days=30)
    for path in legacy_paths:
        if path.exists() and path.stat().st_mtime < cutoff.timestamp():
            logger.info(f"Removing legacy asset: {path}")
            if not dry_run:
                path.unlink()
            removed.append(path)
    return removed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Cleanup legacy assets using clusters")
    parser.add_argument("--clusters", type=Path, default=Path("cluster_output.json"))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    cleanup_legacy_assets(args.clusters, dry_run=args.dry_run)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
