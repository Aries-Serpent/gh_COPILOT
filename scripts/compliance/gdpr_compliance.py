"""GDPR compliance checks and metrics integration.

Implements a basic data-retention audit ensuring records do not exceed
the allowable retention window.
"""

from __future__ import annotations

from typing import Iterable
import argparse

from scripts.compliance.update_compliance_metrics import update_compliance_metrics

DEFAULT_RETENTION_DAYS = 365


def check_data_retention(
    record_ages: Iterable[int],
    limit_days: int = DEFAULT_RETENTION_DAYS,
) -> bool:
    """Return ``True`` if all records are within the retention period."""

    return all(age <= limit_days for age in record_ages)


def main(*, export_dashboard: bool = False) -> float:
    """Run GDPR compliance checks and update composite metrics."""

    # Example record ages (in days) from an audit snapshot.
    record_ages = [100, 200, 300]
    retention_ok = check_data_retention(record_ages)
    details = {"data_retention_within_limit": retention_ok}
    return update_compliance_metrics(
        export_dashboard=export_dashboard,
        report_name="gdpr",
        extra_details=details,
    )


if __name__ == "__main__":  # pragma: no cover
    parser = argparse.ArgumentParser()
    parser.add_argument("--export-dashboard", action="store_true")
    args = parser.parse_args()
    main(export_dashboard=args.export_dashboard)

