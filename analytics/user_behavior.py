"""User behavior analytics utilities."""

from __future__ import annotations

from typing import Sequence

__all__ = ["track_active_users"]


def track_active_users(logins: Sequence[str]) -> int:
    """Return the number of unique user logins."""
    return len(set(logins))
