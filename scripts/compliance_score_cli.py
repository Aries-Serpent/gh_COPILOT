"""CLI for printing the latest compliance score as JSON.

The command reuses :mod:`scripts.compliance_score` helpers to locate the
``analytics.db`` SQLite database and emit the most recent composite score. When
the database or table is missing, the score defaults to ``0``.

Usage::

    python -m scripts.compliance_score_cli --db path/to/analytics.db

If ``--db`` is not supplied, ``analytics.db`` is searched for in the current
directory and then under ``databases/``.
"""

from __future__ import annotations

import argparse
import json

from scripts.compliance_score import _resolve_db_path, fetch_score


def parse_args() -> argparse.Namespace:
    """Return parsed command-line arguments."""

    parser = argparse.ArgumentParser(
        description="Print the latest compliance score as JSON",
    )
    parser.add_argument(
        "--db",
        dest="db_path",
        default=None,
        help="Path to analytics.db (default: search in CWD then databases/)",
    )
    return parser.parse_args()


def main() -> None:
    """Entry point for the compliance score CLI."""

    args = parse_args()
    path = _resolve_db_path(args.db_path)
    score = fetch_score(path) if path else 0.0
    print(json.dumps({"score": score}))


if __name__ == "__main__":  # pragma: no cover - CLI execution
    main()

