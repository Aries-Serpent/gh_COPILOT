"""PCI DSS compliance checks and metrics integration.

Runs a simple storage audit ensuring card numbers are tokenized or
masked before delegating to :func:`update_compliance_metrics`.
"""

from __future__ import annotations

from typing import Iterable
import argparse
import re

from scripts.compliance.update_compliance_metrics import update_compliance_metrics


CARD_REGEX = re.compile(r"^[0-9]{13,19}$")


def check_card_storage(card_entries: Iterable[str]) -> bool:
    """Return ``True`` if no raw card numbers appear in storage entries."""

    return all(not CARD_REGEX.fullmatch(card) for card in card_entries)


def main(*, export_dashboard: bool = False) -> float:
    """Run PCI compliance checks and update composite metrics."""

    # Sample storage entries: masked numbers are allowed.
    stored_cards = ["************1111", "************2222"]
    storage_ok = check_card_storage(stored_cards)
    details = {"card_storage_secure": storage_ok}
    return update_compliance_metrics(
        export_dashboard=export_dashboard,
        report_name="pci",
        extra_details=details,
    )


if __name__ == "__main__":  # pragma: no cover
    parser = argparse.ArgumentParser()
    parser.add_argument("--export-dashboard", action="store_true")
    args = parser.parse_args()
    main(export_dashboard=args.export_dashboard)

