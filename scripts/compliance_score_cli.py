"""CLI for retrieving the latest compliance score.

This thin wrapper reuses :mod:`scripts.compliance_score` to locate the
``analytics.db`` SQLite database and emit the most recent composite score in
JSON form:

.. code-block:: bash

   python -m scripts.compliance_score_cli --db path/to/analytics.db

If no path is provided, the script searches for ``analytics.db`` in the current
directory and then under ``databases/``. When the database or expected table is
missing, the score defaults to ``0``.
"""

from __future__ import annotations

import argparse
import json

from scripts.compliance_score import _resolve_db_path, fetch_score


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

