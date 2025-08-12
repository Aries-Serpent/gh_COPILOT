"""Helpers for integrating with external services."""

from typing import Any, Dict


def integrate_service(service: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Combine ``service`` name and ``payload`` into a single dictionary."""

    result = {"service": service}
    result.update(payload)
    return result


__all__ = ["integrate_service"]

