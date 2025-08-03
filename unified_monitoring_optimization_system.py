"""Utilities for the Unified Monitoring Optimization System.

This module exposes :class:`EnterpriseUtility` from
``scripts.monitoring.unified_monitoring_optimization_system`` and provides a
``push_metrics`` helper used by tests and lightweight integrations to store
arbitrary monitoring metrics in ``analytics.db``.
"""

from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path
from typing import Dict, Optional

from scripts.monitoring.unified_monitoring_optimization_system import EnterpriseUtility

WORKSPACE_ROOT = Path(os.getenv("GH_COPILOT_WORKSPACE", Path.cwd()))
DB_PATH = WORKSPACE_ROOT / "analytics.db"

__all__ = ["EnterpriseUtility", "push_metrics"]


def _ensure_table(conn: sqlite3.Connection, table: str) -> None:
    """Create a simple table for pushed metrics if it does not exist."""
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {table} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            metrics_json TEXT NOT NULL
        )
        """
    )


def push_metrics(
    metrics: Dict[str, float],
    *,
    table: str = "monitoring_metrics",
    db_path: Optional[Path] = None,
) -> None:
    """Store ``metrics`` in ``analytics.db``.

    Parameters
    ----------
    metrics:
        Mapping of metric names to numeric values.
    table:
        Optional table name. Defaults to ``monitoring_metrics``.
    db_path:
        Optional path to the analytics database. If omitted the database in
        ``GH_COPILOT_WORKSPACE`` is used.
    """

    path = db_path or DB_PATH
    with sqlite3.connect(path) as conn:
        _ensure_table(conn, table)
        conn.execute(
            f"INSERT INTO {table} (metrics_json) VALUES (?)",
            (json.dumps(metrics),),
        )
        conn.commit()
