"""Simple real-time synchronization engine.

Provides a change listener, outgoing queue and safe application of
remote updates with conflict detection and idempotency checks.
"""

from __future__ import annotations

import asyncio
import json
from collections import deque
from dataclasses import asdict, dataclass
from typing import Callable, Deque, List, Optional, Set

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

    def __init__(self) -> None:
        self._listeners: List[Callable[[Change], None]] = []
        self.outgoing: Deque[Change] = deque()
        self._applied_ids: Set[str] = set()

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

        while self.outgoing:
            change = self.outgoing.popleft()
            send(change)

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

        if change.id in self._applied_ids:
            return False

        if conflict and conflict(change):
            self._applied_ids.add(change.id)
            return False

        apply(change)
        self._applied_ids.add(change.id)
        return True

    # websocket propagation
    async def _next_outgoing(self) -> Change:
        """Wait for and return the next outgoing change."""

        while not self.outgoing:
            await asyncio.sleep(0.01)
        return self.outgoing.popleft()

    async def open_websocket(self, uri: str, apply: Callable[[Change], None]) -> None:
        """Connect to a websocket ``uri`` and handle bi-directional sync.

        Changes queued via :meth:`notify_change` are sent to the websocket.
        Remote changes received from peers are applied using ``apply``.
        The coroutine runs until cancelled.
        """

        async with websockets.connect(uri) as ws:
            async def sender() -> None:
                try:
                    while True:
                        change = await self._next_outgoing()
                        await ws.send(json.dumps(asdict(change)))
                except (asyncio.CancelledError, ConnectionClosed):
                    pass

            async def receiver() -> None:
                try:
                    async for message in ws:
                        data = json.loads(message)
                        change = Change(**data)
                        self.apply_remote_change(change, apply)
                except (asyncio.CancelledError, ConnectionClosed):
                    pass

            await asyncio.gather(sender(), receiver())
