"""Simple real-time synchronization engine.

Provides a change listener, outgoing queue and safe application of
remote updates with conflict detection and idempotency checks.
"""

from __future__ import annotations

import asyncio
import contextlib
import json
from collections import deque
from dataclasses import dataclass
import logging
from typing import Callable, Deque, Dict, List, Optional, Set

import websockets
from websockets.exceptions import ConnectionClosed


@dataclass(frozen=True)
class Change:
    """Representation of a single change event."""

    id: str
    payload: dict
    timestamp: float


class SyncEngine:
    """Coordinate real-time synchronization with peers."""

    def __init__(self, log_hook: Optional[Callable[[str, Dict[str, object]], None]] = None) -> None:
        self._listeners: List[Callable[[Change], None]] = []
        self.outgoing: Deque[Change] = deque()
        self._applied_ids: Set[str] = set()
        self._log = logging.getLogger("sync")
        self._log_hook = log_hook

    def _emit(self, event: str, **context: object) -> None:
        if event.endswith(".error"):
            self._log.error("%s %s", event, context)
        else:
            self._log.info("%s %s", event, context)
        if self._log_hook:
            self._log_hook(event, context)

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
        self._emit("propagate.start", queued=len(self.outgoing))
        sent = 0
        try:
            while self.outgoing:
                change = self.outgoing.popleft()
                send(change)
                sent += 1
        except Exception as exc:
            self._emit("propagate.error", exception=repr(exc))
            raise
        else:
            self._emit("propagate.end", sent=sent)

    async def open_websocket(self, uri: str, apply: Callable[[Change], None]) -> None:
        """Synchronize with peers over a WebSocket ``uri``.

        Local changes queued via :meth:`notify_change` are broadcast to the
        server, and incoming messages are applied using
        :meth:`apply_remote_change` with the supplied *apply* callback.
        The coroutine runs until the connection is closed or cancelled.
        """

        async with websockets.connect(uri) as websocket:

            async def sender() -> None:
                while True:
                    while self.outgoing:
                        change = self.outgoing.popleft()
                        await websocket.send(
                            json.dumps(
                                {
                                    "id": change.id,
                                    "payload": change.payload,
                                    "timestamp": change.timestamp,
                                }
                            )
                        )
                    await asyncio.sleep(0.01)

            async def receiver() -> None:
                async for message in websocket:
                    data = json.loads(message)
                    change = Change(
                        id=data["id"],
                        payload=data["payload"],
                        timestamp=data["timestamp"],
                    )
                    self.apply_remote_change(change, apply)

            send_task = asyncio.create_task(sender())
            try:
                await receiver()
            except ConnectionClosed:
                pass
            finally:
                send_task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await send_task

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

        self._emit("apply.start", id=change.id)
        try:
            if change.id in self._applied_ids:
                self._emit("apply.end", id=change.id, status="duplicate")
                return False

            if conflict and conflict(change):
                self._applied_ids.add(change.id)
                self._emit("apply.end", id=change.id, status="conflict")
                return False

            apply(change)
            self._applied_ids.add(change.id)
            self._emit("apply.end", id=change.id, status="applied")
            return True
        except Exception as exc:
            self._emit("apply.error", id=change.id, exception=repr(exc))
            raise


# CODEx: log_analytics_event integration hint
try:
    from tools.apply_analytics_event_workflow import log_analytics_event  # lazy import for optional use
except Exception:
    log_analytics_event = None
# Example (wrap at success/failure boundaries):
# if log_analytics_event:
#     log_analytics_event(run_id, 'sync', {'status': 'ok', 'file': __file__})
