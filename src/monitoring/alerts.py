from __future__ import annotations

"""Alert dispatching tied into recovery handlers."""

from typing import Callable, Dict, Iterable

from ..recovery.handlers import (
    FAILURE_PATTERNS,
    handle_auth_error,
    handle_db_disconnect,
    handle_failed_sync,
)

AlertHandler = Callable[..., bool]

ALERT_HANDLERS: Dict[str, AlertHandler] = {
    "db_disconnect": handle_db_disconnect,
    "sync_failed": handle_failed_sync,
    "auth_error": handle_auth_error,
}


def dispatch_alert(alert_type: str, **callbacks) -> bool:
    """Dispatch an alert to its corresponding recovery handler.

    Parameters
    ----------
    alert_type:
        Type of alert to dispatch. Must be one of ``db_disconnect``,
        ``sync_failed`` or ``auth_error``.
    callbacks:
        Keyword arguments expected by the handler, such as ``reconnect`` for
        database disconnects, ``resync`` for synchronization failures and
        ``refresh_token`` for authentication errors.

    Returns
    -------
    bool
        ``True`` if recovery succeeded, ``False`` otherwise.
    """
    handler = ALERT_HANDLERS.get(alert_type)
    if handler is None:
        return False
    try:
        return handler(**callbacks)
    except Exception:
        return False


def monitor_failures(
    lines: Iterable[str], callbacks: Dict[str, Callable[[], bool]]
) -> Dict[str, bool]:
    """Scan log lines and trigger recovery routines when patterns match."""

    results: Dict[str, bool] = {}
    for line in lines:
        for pattern in FAILURE_PATTERNS:
            if pattern.regex.search(line):
                action = callbacks.get(pattern.name)
                if action is None:
                    results[pattern.name] = False
                else:
                    results[pattern.name] = pattern.routine(action)
    return results
