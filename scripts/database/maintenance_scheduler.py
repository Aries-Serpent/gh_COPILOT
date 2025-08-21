#!/usr/bin/env python3
"""Periodically synchronize databases and verify size compliance."""

from __future__ import annotations

import argparse
import logging
import signal
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

from tqdm import tqdm

from utils.validation_utils import anti_recursion_guard, validate_enterprise_environment

from scripts.database.cross_database_sync_logger import log_sync_operation
from scripts.database.database_sync_scheduler import synchronize_databases
from scripts.database.size_compliance_checker import check_database_sizes
from gh_copilot.auditor.consistency import run_audit

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


def run_cycle(workspace: Path, *, timeout: int | None = None) -> None:
    """Synchronize replicas, check sizes, and audit asset consistency."""
    db_dir = workspace / "databases"
    master = db_dir / "enterprise_assets.db"
    list_path = workspace / "documentation" / "CONSOLIDATED_DATABASE_LIST.md"
    replica_names = _load_database_names(list_path)
    replicas = [db_dir / name for name in replica_names if name != master.name]
    log_db = db_dir / "enterprise_assets.db"
    production_db = db_dir / "production.db"
    analytics_db = db_dir / "analytics.db"

    start_dt = datetime.now(timezone.utc)
    log_sync_operation(log_db, f"cycle_start_{start_dt.isoformat()}")
    etc = start_dt + timedelta(seconds=len(replicas) + 1)
    log_sync_operation(log_db, f"cycle_estimated_complete_{etc.isoformat()}")

    status = "success"
    start_ts = time.time()
    try:
        with tqdm(total=3, desc="Maintenance Cycle", unit="task", dynamic_ncols=True) as bar:
            synchronize_databases(
                master,
                replicas,
                log_db=log_db,
                timeout=timeout,
            )
            etc_delta = bar.format_dict.get("elapsed", 0) + bar.format_dict.get("remaining", 0)
            etc_time = start_dt + timedelta(seconds=etc_delta)
            bar.set_postfix_str(f"ETC {etc_time.strftime('%H:%M:%S')}")
            bar.update(1)
            if timeout and time.time() - start_ts > timeout:
                status = "timeout"
                raise TimeoutError("Maintenance cycle timed out")
            check_database_sizes(db_dir)
            etc_delta = bar.format_dict.get("elapsed", 0) + bar.format_dict.get("remaining", 0)
            etc_time = start_dt + timedelta(seconds=etc_delta)
            bar.set_postfix_str(f"ETC {etc_time.strftime('%H:%M:%S')}")
            bar.update(1)
            if timeout and time.time() - start_ts > timeout:
                status = "timeout"
                raise TimeoutError("Maintenance cycle timed out")
            run_audit(
                master,
                production_db,
                analytics_db,
                [workspace],
            )
            etc_delta = bar.format_dict.get("elapsed", 0) + bar.format_dict.get("remaining", 0)
            etc_time = start_dt + timedelta(seconds=etc_delta)
            bar.set_postfix_str(f"ETC {etc_time.strftime('%H:%M:%S')}")
            bar.update(1)
    except TimeoutError:
        status = "timeout"
    except Exception as exc:
        status = f"failed_{type(exc).__name__}"
        raise
    finally:
        log_sync_operation(log_db, f"cycle_status_{status}", start_time=start_dt)


@anti_recursion_guard
def main(workspace: Path, interval: int, once: bool = False, timeout: int | None = None) -> None:
    """Run maintenance cycles at a fixed interval."""
    validate_enterprise_environment()

    def handle_signal(signum, frame):
        nonlocal running
        logger.info("Received termination signal. Shutting down...")
        running = False

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    running = True
    while running:
        try:
            run_cycle(workspace, timeout=timeout)
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
    parser.add_argument("--timeout", type=int, help="Abort cycle if it exceeds this many seconds")
    args = parser.parse_args()
    main(args.workspace, args.interval, args.once, args.timeout)
