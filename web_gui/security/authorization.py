"""Simple role-based authorization helpers."""

from __future__ import annotations

import logging
from functools import wraps
from typing import Callable, Iterable

from flask import Flask, Response, g

from secondary_copilot_validator import SecondaryCopilotValidator

logger = logging.getLogger(__name__)


def init_app(app: Flask) -> None:
    """Initialize authorization configuration for *app*."""

    # currently no default config; placeholder for symmetry
    app.config.setdefault("AUTHORIZATION_ENABLED", True)


def has_role(
    user_roles: Iterable[str],
    required_role: str,
    validator: SecondaryCopilotValidator | None = None,
) -> bool:
    """Return ``True`` if ``required_role`` is present in ``user_roles``."""

    allowed = required_role in set(user_roles)
    if not allowed:
        logger.warning("Missing required role: %s", required_role)
    (validator or SecondaryCopilotValidator()).validate_corrections([str(allowed)])
    return allowed


def requires_role(role: str) -> Callable[[Callable[..., Response]], Callable[..., Response]]:
    """Decorator that ensures the current user has *role*."""

    def decorator(func: Callable[..., Response]) -> Callable[..., Response]:
        @wraps(func)
        def wrapper(*args, **kwargs):
            if role not in getattr(g, "current_roles", set()):
                logger.warning("Access denied, missing role %s", role)
                return Response("Forbidden", status=403)
            return func(*args, **kwargs)

        return wrapper

    return decorator


__all__ = ["init_app", "has_role", "requires_role"]
