"""Simple role-based authorization helpers."""

from __future__ import annotations

from functools import wraps
from typing import Callable, Iterable

from flask import Flask, g, request, Response


def init_app(app: Flask) -> None:
    """Load user roles from ``USER_ROLES`` mapping using request token."""
    app.config.setdefault("USER_ROLES", {})

    @app.before_request
    def _load_roles() -> None:
        token = request.headers.get("Authorization", "").removeprefix("Bearer ")
        roles: Iterable[str] = app.config["USER_ROLES"].get(token, [])
        g.current_roles = set(roles)


def requires_role(role: str) -> Callable[[Callable[..., Response]], Callable[..., Response]]:
    """Decorator that ensures the current user has *role*."""

    def decorator(func: Callable[..., Response]) -> Callable[..., Response]:
        @wraps(func)
        def wrapper(*args, **kwargs):
            if role not in getattr(g, "current_roles", set()):
                return Response("Forbidden", status=403)
            return func(*args, **kwargs)

        return wrapper

    return decorator


__all__ = ["init_app", "requires_role"]
