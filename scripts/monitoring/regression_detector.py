#!/usr/bin/env python3
"""Detect regressions in performance metrics using a simple moving average."""

from __future__ import annotations

import argparse
import sqlite3
import time
from pathlib import Path
from typing import Iterable, List, Tuple

__all__ = ["main", "detect_regressions"]


def detect_regressions(
    values: Iterable[float],
    window: int,
    threshold: float,
) -> List[Tuple[int, float, float]]:
    """Return list of ``(index, value, sma)`` where a regression is detected."""

    vals = list(values)
    results: List[Tuple[int, float, float]] = []
    for idx in range(window, len(vals)):
        sma = sum(vals[idx - window : idx]) / window
        if vals[idx] > sma + threshold:
            results.append((idx, vals[idx], sma))
    return results


def _persist(db_path: Path, rows: List[Tuple[int, float, float]]) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS regressions (ts REAL, idx INTEGER, value REAL, sma REAL)"
        )
        conn.executemany(
            "INSERT INTO regressions (ts, idx, value, sma) VALUES (?, ?, ?, ?)",
            [(time.time(), idx, val, sma) for idx, val, sma in rows],
        )
        conn.commit()


def main(argv: list[str] | None = None) -> int:
    """CLI entry point for regression detection."""

    ap = argparse.ArgumentParser(description="Detect metric regressions")
    ap.add_argument("--metric-file", type=Path, required=True, help="Metric history file")
    ap.add_argument("--window", type=int, default=3, help="Window size for moving average")
    ap.add_argument(
        "--threshold", type=float, default=10.0, help="Trigger alert if value exceeds SMA + threshold"
    )
    ap.add_argument(
        "--db-path", type=Path, default=Path("analytics.db"), help="Analytics SQLite DB"
    )
    ns = ap.parse_args(argv)

    values = [float(line.strip()) for line in ns.metric_file.read_text().splitlines() if line.strip()]
    rows = detect_regressions(values, ns.window, ns.threshold)
    if rows:
        _persist(ns.db_path, rows)
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

