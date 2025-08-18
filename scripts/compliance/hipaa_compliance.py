"""HIPAA compliance checks and metrics integration.

Performs a simple Protected Health Information (PHI) access audit by
verifying that only authorized users appear in access logs.
"""

from __future__ import annotations

from typing import Iterable, Set
import argparse

from scripts.compliance.update_compliance_metrics import update_compliance_metrics


def check_phi_access(log_users: Iterable[str], allowed_users: Set[str]) -> bool:
    """Return ``True`` if all PHI accesses are by authorized personnel."""

    return all(user in allowed_users for user in log_users)


def main(*, export_dashboard: bool = False) -> float:
    """Run HIPAA compliance checks and update composite metrics."""

    # Example log and policy; real implementations would query audit tables.
    access_log = ["alice", "bob"]
    allowed = {"alice", "bob", "carol"}
    phi_ok = check_phi_access(access_log, allowed)
    details = {"phi_access_authorized": phi_ok}
    return update_compliance_metrics(
        export_dashboard=export_dashboard,
        report_name="hipaa",
        extra_details=details,
    )


if __name__ == "__main__":  # pragma: no cover
    parser = argparse.ArgumentParser()
    parser.add_argument("--export-dashboard", action="store_true")
    args = parser.parse_args()
    main(export_dashboard=args.export_dashboard)

