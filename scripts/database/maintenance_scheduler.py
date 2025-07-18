#!/usr/bin/env python3
"""Periodically synchronize databases and verify size compliance."""
from __future__ import annotations

import argparse
import logging
import signal
import time
from pathlib import Path

from .database_sync_scheduler import synchronize_databases
from .size_compliance_checker import check_database_sizes

logger = logging.getLogger(__name__)


def configure_logging():
    """Configure logging for the script."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def _load_database_names(list_file: Path) -> list[str]:
    """Return database names listed in the markdown file.

    Lines may include comments after a ``#`` which are ignored.
    """
    names: list[str] = []
    for line in list_file.read_text().splitlines():
        line = line.strip()
        if line.startswith("- "):
            name = line[2:]
            name = name.split("#", 1)[0].strip()
            if name:
                names.append(name)
    return names


def run_cycle(workspace: Path) -> None:
    """Synchronize replicas and check database sizes."""
    db_dir = workspace / "databases"
    master = db_dir / "production.db"
    list_path = workspace / "documentation" / "CONSOLIDATED_DATABASE_LIST.md"
    replica_names = _load_database_names(list_path)
    replicas = [db_dir / name for name in replica_names if name != master.name]
    log_db = db_dir / "enterprise_assets.db"
    synchronize_databases(master, replicas, log_db=log_db)
    check_database_sizes(db_dir)


def main(workspace: Path, interval: int, once: bool = False) -> None:
    """Run maintenance cycles at a fixed interval."""
    def handle_signal(signum, frame):
        nonlocal running
        logger.info("Received termination signal. Shutting down...")
        running = False

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    running = True
    while running:
        try:
            run_cycle(workspace)
        except Exception as e:
            logger.error("An error occurred during the maintenance cycle: %s", e, exc_info=True)
        if once:
            break
        try:
            time.sleep(interval * 60)
        except InterruptedError:
            logger.info("Sleep interrupted. Exiting loop.")
            break


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Periodic database maintenance")
    parser.add_argument("--workspace", type=Path, default=Path("."), help="Workspace root")
    parser.add_argument("--interval", type=int, default=60, help="Minutes between cycles")
    parser.add_argument("--once", action="store_true", help="Run a single maintenance cycle")
    args = parser.parse_args()
    main(args.workspace, args.interval, args.once)
