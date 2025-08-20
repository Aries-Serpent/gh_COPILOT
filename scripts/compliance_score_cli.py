"""CLI for retrieving the latest compliance score.

This thin wrapper reuses :mod:`scripts.compliance_score` to locate the
``analytics.db`` SQLite database and emit the most recent composite score in
JSON form:

.. code-block:: bash

   python scripts/compliance_score_cli.py --db path/to/analytics.db

If no path is provided, the script searches for ``analytics.db`` in the current
directory and then under ``databases/``. When the database or expected table is
missing, the score defaults to ``0``.
"""

from __future__ import annotations

import argparse
import json

import sys
from pathlib import Path

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from scripts.compliance_score import _resolve_db_path, fetch_score
else:  # pragma: no cover - executed when run as module
    from .compliance_score import _resolve_db_path, fetch_score


def main() -> None:
    """Entry point for the compliance score CLI."""

    parser = argparse.ArgumentParser(
        description="Print the latest compliance score in JSON"
    )
    parser.add_argument(
        "--db", dest="db_path", default=None, help="Path to analytics.db"
    )
    args = parser.parse_args()

    path = _resolve_db_path(args.db_path)
    score = fetch_score(path) if path else 0.0
    print(json.dumps({"score": score}))


if __name__ == "__main__":  # pragma: no cover - CLI execution
    main()

