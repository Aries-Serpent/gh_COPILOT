"""Monitor composite compliance scores and trigger alerts when low."""

from __future__ import annotations

import time
from pathlib import Path

from enterprise_modules.compliance import get_latest_compliance_score
from notifications import email, webhook

THRESHOLD = 0.8


def check_compliance(db_path: Path | None = None) -> float:
    """Return the latest score and send alerts if below threshold."""
    score = get_latest_compliance_score(db_path)
    if score < THRESHOLD:
        message = f"Compliance score below threshold: {score:.2f}"
        email.send_alert(message)
        webhook.send_alert(message)
    return score


def monitor_forever(interval: int = 60) -> None:  # pragma: no cover - loop
    """Continuously monitor compliance scores at the given interval."""
    while True:
        check_compliance()
        time.sleep(interval)


__all__ = ["check_compliance", "monitor_forever", "THRESHOLD"]

