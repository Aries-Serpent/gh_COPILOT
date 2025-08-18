#!/usr/bin/env python3
"""Analyze historical performance metrics.

The analyzer reads a newline separated list of metric values from a file and
performs a simple trend analysis. If the latest value breaches a supplied
threshold the program exits with a non-zero status code.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from statistics import mean

__all__ = ["main", "load_metrics", "analyze_trend"]


def load_metrics(path: Path) -> list[float]:
    """Load metric values from ``path``."""

    return [float(line.strip()) for line in path.read_text().splitlines() if line.strip()]


def analyze_trend(values: list[float]) -> float:
    """Return the difference between last and first metric values."""

    if not values:
        raise ValueError("no metric values supplied")
    return values[-1] - values[0]


def main(argv: list[str] | None = None) -> int:
    """CLI entry point for performance analysis."""

    ap = argparse.ArgumentParser(description="Analyze metric trends")
    ap.add_argument("--metric-file", type=Path, required=True, help="File containing metric values")
    ap.add_argument("--threshold", type=float, default=80.0, help="Alert threshold for latest metric")
    ns = ap.parse_args(argv)

    values = load_metrics(ns.metric_file)
    trend = analyze_trend(values)
    latest = values[-1]
    avg = mean(values)
    print(f"trend={trend:.2f} average={avg:.2f} latest={latest:.2f}")
    if latest >= ns.threshold:
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

