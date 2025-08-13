#!/usr/bin/env python3
"""Database reconciliation utilities.

This module scans multiple SQLite databases for drift in the
``cross_database_sync_operations`` table and attempts simple healing by
copying missing rows.  It logs reconciliation operations using
``cross_database_sync_logger.log_sync_operation`` and emits warnings for
schema mismatches.

The script is intentionally lightweight – it performs a best-effort copy
without guaranteeing full transactional consistency, but it provides a
foundation for future enhancements such as detailed diffing and
rollback support.
"""

from __future__ import annotations

import logging
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple

from enterprise_modules.compliance import validate_enterprise_operation
from utils.logging_utils import log_enterprise_operation, setup_enterprise_logging

from .cross_database_sync_logger import log_sync_operation


logger = logging.getLogger(__name__)


@dataclass
class DBState:
    path: Path
    rows: List[Tuple]


def _fetch_operations(conn: sqlite3.Connection) -> List[Tuple]:
    cur = conn.execute(
        "SELECT operation, status, start_time, duration, timestamp FROM cross_database_sync_operations"
    )
    return [tuple(row) for row in cur.fetchall()]


def reconcile_once(db_paths: Sequence[Path]) -> None:
    """Run a single reconciliation cycle across ``db_paths``.

    Any rows missing from a database are copied from the first database in the
    list.  Schema mismatches are reported via the enterprise logging system.
    """
    validate_enterprise_operation()

    states: List[DBState] = []
    connections: List[sqlite3.Connection] = []
    for path in db_paths:
        conn = sqlite3.connect(path)
        connections.append(conn)
        rows = []
        try:
            rows = _fetch_operations(conn)
        except sqlite3.OperationalError:
            # Table missing – schema drift.
            log_enterprise_operation(
                "schema_mismatch", "WARNING", f"missing cross_database_sync_operations in {path}"
            )
        states.append(DBState(path, rows))

    if not states or not states[0].rows:
        for conn in connections:
            conn.close()
        return

    source_rows = set(states[0].rows)
    for state, conn in zip(states[1:], connections[1:]):
        existing_map = {(r[0], r[4]): r for r in state.rows}
        missing = source_rows.difference(state.rows)
        if not missing:
            continue
        log_enterprise_operation(
            "drift_detected",
            "WARNING",
            f"{len(missing)} rows missing in {state.path}",
        )
        conn.execute("BEGIN")
        try:
            for row in missing:
                op, status, start_time, duration, ts = row
                existing = existing_map.get((op, ts))
                if existing and existing != row:
                    diff = {
                        idx: (old, new)
                        for idx, (old, new) in enumerate(zip(existing, row))
                        if old != new
                    }
                    log_enterprise_operation(
                        "row_conflict",
                        "ERROR",
                        f"conflict for {op} at {state.path}: {diff}",
                    )
                    raise ValueError("conflicting row")
                log_enterprise_operation(
                    "row_diff",
                    "INFO",
                    f"inserting {row} into {state.path}",
                )
                conn.execute(
                    "INSERT INTO cross_database_sync_operations (operation, status, start_time, duration, timestamp) "
                    "VALUES (?, ?, ?, ?, ?)",
                    row,
                )
            conn.commit()
        except Exception:
            conn.rollback()
            log_enterprise_operation(
                "reconcile_rollback",
                "ERROR",
                f"rolled back reconciliation for {state.path}",
            )

    for conn in connections:
        conn.close()

    log_sync_operation(list(db_paths), "reconcile_databases", status="SUCCESS")


def run_reconciler(
    db_paths: Iterable[Path], *, interval: int = 60, cycles: int = 1
) -> None:
    """Periodically invoke :func:`reconcile_once`.

    Parameters
    ----------
    db_paths:
        Paths to databases to reconcile.
    interval:
        Seconds to wait between cycles.
    cycles:
        Number of reconciliation cycles to execute.  ``0`` runs indefinitely.
    """

    paths = [Path(p) for p in db_paths]
    count = 0
    while cycles == 0 or count < cycles:
        reconcile_once(paths)
        count += 1
        if cycles == 0 or count < cycles:
            time.sleep(interval)


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Cross-database reconciler")
    parser.add_argument(
        "--database",
        nargs="+",
        type=Path,
        default=[
            Path("databases/production.db"),
            Path("databases/analytics.db"),
            Path("databases/template_intelligence.db"),
        ],
        help="Paths to databases",
    )
    parser.add_argument("--interval", type=int, default=60, help="Seconds between cycles")
    parser.add_argument(
        "--cycles",
        type=int,
        default=1,
        help="Number of cycles (0 for continuous)",
    )

    args = parser.parse_args()
    setup_enterprise_logging()
    run_reconciler(args.database, interval=args.interval, cycles=args.cycles)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

