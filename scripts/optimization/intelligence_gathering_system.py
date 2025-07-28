"""Gather unified analytics and predictive insights."""
from __future__ import annotations

import argparse
import logging
import os
import sqlite3
from pathlib import Path

from tqdm import tqdm
from utils.log_utils import _log_event

__all__ = ["IntelligenceGatheringSystem", "parse_args", "main"]


class IntelligenceGatheringSystem:
    """Gather unified analytics and predictive insights."""

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.logger = logging.getLogger(__name__)

    def gather(self) -> None:
        """Gather analytics from ``production.db``."""
        self.logger.info("Gathering intelligence from %s", self.db_path)
        analytics_db = Path(os.getenv("GH_COPILOT_WORKSPACE", ".")) / "databases" / "analytics.db"
        cur = self.conn.cursor()
        tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'")]
        with tqdm(tables, desc="Collecting", unit="table") as bar:
            for tbl in bar:
                bar.set_postfix(table=tbl)
                try:
                    count = cur.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]
                except sqlite3.Error:
                    count = 0
                _log_event(
                    {"event": "table_summary", "table": tbl, "rows": count},
                    table="intel_reports",
                    db_path=analytics_db,
                )
        self.logger.info("Gathered metrics for %d tables", len(tables))


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Gather analytics")
    parser.add_argument(
        "db_path",
        nargs="?",
        type=Path,
        default=Path(os.getenv("GH_COPILOT_WORKSPACE", ".")) / "databases" / "production.db",
        help="Path to production database",
    )
    return parser.parse_args(args)


def main(args: list[str] | None = None) -> int:
    ns = parse_args(args)
    IntelligenceGatheringSystem(ns.db_path).gather()
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
