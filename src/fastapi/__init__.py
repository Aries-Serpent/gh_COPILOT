"""Minimal FastAPI stub for tests.

This module provides tiny stand-ins for the pieces of FastAPI used in the
project's test suite. It is **not** a full implementation of FastAPI.
"""

from __future__ import annotations

from typing import Any, Callable


class BackgroundTasks:  # pragma: no cover - simple placeholder
    pass


class FastAPI:  # pragma: no cover - minimal app container
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        pass

    def get(self, path: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            return func
        return decorator

    def post(self, path: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            return func
        return decorator


def Query(default: Any = None, **_: Any) -> Any:
    """Return ``default``; placeholder for FastAPI's Query."""

    return default


__all__ = ["BackgroundTasks", "FastAPI", "Query"]
