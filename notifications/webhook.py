"""Webhook notification stub for compliance alerts."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def send_alert(message: str) -> None:
    """Log a compliance alert webhook.

    Replace with actual HTTP POST in production environments.
    """
    logger.warning("WEBHOOK ALERT: %s", message)


__all__ = ["send_alert"]

