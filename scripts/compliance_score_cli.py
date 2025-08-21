#!/usr/bin/env python3
"""Print the latest compliance score from ``analytics.db``.

This small CLI reads the ``compliance_scores`` table in the analytics
database and outputs the most recent ``composite_score`` value as JSON.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path


DEFAULT_DB_PATH = Path("databases/analytics.db")


def get_score(db_path: Path) -> float:
    """Return the latest composite score from ``db_path``.

    If the database or table is missing, ``0.0`` is returned.
    """

    if not db_path.exists():
        return 0.0
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.execute(
                "SELECT composite_score FROM compliance_scores "
                "ORDER BY timestamp DESC LIMIT 1"
            )
            row = cursor.fetchone()
            return float(row[0]) if row else 0.0
    except sqlite3.Error:
        return 0.0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Print latest compliance score from analytics.db"
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=DEFAULT_DB_PATH,
        help="Path to analytics.db (default: %(default)s)",
    )
    args = parser.parse_args()

    score = get_score(args.db)
    print(json.dumps({"score": score}))


if __name__ == "__main__":
    main()
