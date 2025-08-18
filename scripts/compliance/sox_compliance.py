"""SOX compliance checks and metrics integration.

This module performs a minimal financial control audit before delegating
to :func:`update_compliance_metrics`. The audit asserts that all recorded
transactions fall below a configurable threshold representing
management-approved limits.
"""

from __future__ import annotations

from typing import Iterable
import argparse

from scripts.compliance.update_compliance_metrics import update_compliance_metrics

DEFAULT_TRANSACTION_LIMIT = 1_000_000.0


def check_financial_controls(
    transactions: Iterable[float],
    limit: float = DEFAULT_TRANSACTION_LIMIT,
) -> bool:
    """Return ``True`` if all transactions are within the SOX threshold."""

    return all(t <= limit for t in transactions)


def main(*, export_dashboard: bool = False) -> float:
    """Run SOX compliance checks and update composite metrics."""

    # In a real system these transactions would come from a ledger query.
    sample_transactions = [5000.0, 125000.0, 750000.0]
    controls_ok = check_financial_controls(sample_transactions)
    details = {"financial_controls_passed": controls_ok}
    return update_compliance_metrics(
        export_dashboard=export_dashboard,
        report_name="sox",
        extra_details=details,
    )


if __name__ == "__main__":  # pragma: no cover
    parser = argparse.ArgumentParser()
    parser.add_argument("--export-dashboard", action="store_true")
    args = parser.parse_args()
    main(export_dashboard=args.export_dashboard)

