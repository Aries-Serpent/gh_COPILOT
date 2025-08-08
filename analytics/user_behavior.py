"""Utilities for tracking user actions."""

from __future__ import annotations

from typing import Dict, Iterable

__all__ = ["log_user_action", "track_active_users"]


def log_user_action(action: str, storage: Dict[str, int] | None = None) -> Dict[str, int]:
    """Record an ``action`` count in ``storage`` and return the updated mapping."""
    store = storage if storage is not None else {}
    store[action] = store.get(action, 0) + 1
    return store


def track_active_users(actions: Iterable[str]) -> int:
    """Return the number of unique users represented in ``actions``."""

    return len(set(actions))
