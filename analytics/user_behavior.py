"""Utilities for tracking user actions."""

from __future__ import annotations

from typing import Dict

__all__ = ["log_user_action"]


def log_user_action(action: str, storage: Dict[str, int] | None = None) -> Dict[str, int]:
    """Record an ``action`` count in ``storage`` and return the updated mapping."""
    store = storage if storage is not None else {}
    store[action] = store.get(action, 0) + 1
    return store
