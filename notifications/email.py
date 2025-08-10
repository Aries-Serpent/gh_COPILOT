"""Email notification stub for compliance alerts."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def send_alert(message: str) -> None:
    """Log a compliance alert email.

    This placeholder can be replaced with a real SMTP integration.
    """
    logger.warning("EMAIL ALERT: %s", message)


__all__ = ["send_alert"]

