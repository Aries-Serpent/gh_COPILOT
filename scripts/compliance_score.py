"""Fetch the latest compliance score from ``analytics.db``.

This helper looks for a SQLite database named ``analytics.db`` (either in the
current working directory or under ``databases/``) and prints the most recent
composite compliance score as JSON in the form ``{"score": value}``.

The database is expected to contain a table named
``compliance_metrics_history`` with a ``composite_score`` column. If the
database or table is missing, or the file is not a valid SQLite database, the
score defaults to ``0``.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path
from typing import Iterable, Optional


def _resolve_db_path(explicit: Optional[str]) -> Optional[Path]:
    """Return the first existing analytics database path.

    The search order is:

    1. ``explicit`` path provided via ``--db`` argument
    2. ``analytics.db`` in the current working directory
    3. ``databases/analytics.db`` relative to the current working directory
    """

    candidates: Iterable[Path] = []
    if explicit:
        candidates = [Path(explicit)]
    else:
        candidates = [Path("analytics.db"), Path("databases") / "analytics.db"]
    for path in candidates:
        if path.exists():
            return path
    return None


def fetch_score(db_path: Path) -> float:
    """Return the most recent composite compliance score from ``db_path``.

    If the database cannot be read, ``0.0`` is returned.
    """

    try:
        with sqlite3.connect(str(db_path)) as conn:
            cur = conn.execute(
                "SELECT composite_score FROM compliance_metrics_history ORDER BY ts DESC LIMIT 1"
            )
            row = cur.fetchone()
            if row and row[0] is not None:
                return float(row[0])
    except sqlite3.Error:
        # Includes OperationalError and DatabaseError when the file is not a DB.
        pass
    return 0.0


def main() -> None:
    parser = argparse.ArgumentParser(description="Print latest compliance score")
    parser.add_argument(
        "--db", dest="db_path", default=None, help="Path to analytics.db"
    )
    args = parser.parse_args()

    path = _resolve_db_path(args.db_path)
    score = fetch_score(path) if path else 0.0
    print(json.dumps({"score": score}))


if __name__ == "__main__":
    main()

