from __future__ import annotations

"""Recovery handlers for common operational failures."""

import re
from dataclasses import dataclass
from typing import Callable, Iterable, Pattern

from . import routines


@dataclass
class FailurePattern:
    """Pattern that triggers a recovery routine."""

    name: str
    regex: Pattern[str]
    routine: Callable[[Callable[[], bool]], bool]


FAILURE_PATTERNS: Iterable[FailurePattern] = (
    FailurePattern(
        "service_crash",
        re.compile(r"service\s+.*down", re.IGNORECASE),
        routines.restart_service,
    ),
    FailurePattern(
        "state_corruption",
        re.compile(r"state\s+.*corrupt", re.IGNORECASE),
        routines.revert_state,
    ),
)


def handle_db_disconnect(reconnect: Callable[[], bool], *, retries: int = 3) -> bool:
    """Recover from a database disconnect by retrying ``reconnect``.

    Parameters
    ----------
    reconnect:
        Callback that attempts to re-establish the database connection.
    retries:
        Number of attempts before giving up. Defaults to ``3``.
    """
    for _ in range(retries):
        try:
            if reconnect():
                return True
        except Exception:
            continue
    return False


def handle_failed_sync(resync: Callable[[], bool], *, retries: int = 3) -> bool:
    """Recover from a failed synchronization by retrying ``resync``.

    Parameters
    ----------
    resync:
        Callback that attempts to perform the synchronization.
    retries:
        Number of attempts before giving up. Defaults to ``3``.
    """
    for _ in range(retries):
        try:
            if resync():
                return True
        except Exception:
            continue
    return False


def handle_auth_error(refresh_token: Callable[[], bool], *, retries: int = 2) -> bool:
    """Recover from an authentication error by refreshing credentials.

    Parameters
    ----------
    refresh_token:
        Callback that refreshes authentication tokens.
    retries:
        Number of attempts before giving up. Defaults to ``2``.
    """
    for _ in range(retries):
        try:
            if refresh_token():
                return True
        except Exception:
            continue
    return False
