from __future__ import annotations

"""Compliance aggregator for composite score calculations.

This utility combines lint, test, and placeholder metrics into a
weighted composite score and records the results for dashboard use.
"""

from pathlib import Path
import argparse
from typing import Any, Dict

from enterprise_modules.compliance import (
    calculate_composite_score,
    record_code_quality_metrics,
)


def aggregate_metrics(
    ruff_issues: int,
    tests_passed: int,
    tests_failed: int,
    placeholders_open: int,
    placeholders_resolved: int = 0,
    *,
    db_path: Path | None = None,
    test_mode: bool = False,
) -> Dict[str, Any]:
    """Return composite compliance metrics and optionally persist them."""
    composite, breakdown = calculate_composite_score(
        ruff_issues,
        tests_passed,
        tests_failed,
        placeholders_open,
        placeholders_resolved,
    )
    breakdown = {
        "lint_score": breakdown["lint_score"],
        "test_score": breakdown["test_score"],
        "placeholder_score": breakdown["placeholder_score"],
    }

    record_code_quality_metrics(
        ruff_issues,
        tests_passed,
        tests_failed,
        placeholders_open,
        placeholders_resolved,
        db_path,
        test_mode=test_mode,
    )
    result: Dict[str, Any] = {
        "ruff_issues": ruff_issues,
        "tests_passed": tests_passed,
        "tests_failed": tests_failed,
        "placeholders_open": placeholders_open,
        "placeholders_resolved": placeholders_resolved,
        "composite_score": composite,
        "breakdown": breakdown,
    }
    return result


def main() -> None:  # pragma: no cover - CLI wrapper
    parser = argparse.ArgumentParser(description="Compute composite compliance score")
    parser.add_argument("--ruff-issues", type=int, required=True)
    parser.add_argument("--tests-passed", type=int, required=True)
    parser.add_argument("--tests-failed", type=int, required=True)
    parser.add_argument("--placeholders-open", type=int, required=True)
    parser.add_argument("--placeholders-resolved", type=int, default=0)
    parser.add_argument("--db-path", type=Path)
    args = parser.parse_args()
    metrics = aggregate_metrics(
        args.ruff_issues,
        args.tests_passed,
        args.tests_failed,
        args.placeholders_open,
        args.placeholders_resolved,
        db_path=args.db_path,
    )
    print(metrics)


if __name__ == "__main__":  # pragma: no cover - CLI execution
    main()
