"""Simple real-time synchronization engine.

Provides a change listener, outgoing queue and safe application of
remote updates with conflict detection and idempotency checks.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import logging
from typing import Callable, Deque, List, Optional, Set


@dataclass(frozen=True)
class Change:
    """Representation of a single change event."""

    id: str
    payload: dict
    timestamp: float


class SyncEngine:
    """Coordinate real-time synchronization with peers."""

    def __init__(self) -> None:
        self._listeners: List[Callable[[Change], None]] = []
        self.outgoing: Deque[Change] = deque()
        self._applied_ids: Set[str] = set()
        self._log = logging.getLogger("sync")

    # change-listener
    def register_listener(self, callback: Callable[[Change], None]) -> None:
        """Register a *callback* to be notified of local changes."""

        self._listeners.append(callback)

    def notify_change(self, change: Change) -> None:
        """Record a local change and notify listeners."""

        self.outgoing.append(change)
        for cb in list(self._listeners):
            cb(change)

    # outgoing queue propagation
    def propagate(self, send: Callable[[Change], None]) -> None:
        """Send queued changes to peers using ``send`` and clear the queue."""
        self._log.info("start")
        try:
            while self.outgoing:
                change = self.outgoing.popleft()
                send(change)
        except Exception:
            self._log.exception("error")
            raise
        else:
            self._log.info("end")

    # idempotent remote apply with conflict detection
    def apply_remote_change(
        self,
        change: Change,
        apply: Callable[[Change], None],
        conflict: Optional[Callable[[Change], bool]] = None,
    ) -> bool:
        """Apply a remote *change* if safe.

        Returns ``True`` if the change was applied locally, ``False`` if the
        change was ignored because it was already processed or a conflict was
        detected.
        """

        self._log.info("start")
        try:
            if change.id in self._applied_ids:
                self._log.info("end")
                return False

            if conflict and conflict(change):
                self._applied_ids.add(change.id)
                self._log.info("end")
                return False

            apply(change)
            self._applied_ids.add(change.id)
            self._log.info("end")
            return True
        except Exception:
            self._log.exception("error")
            raise
