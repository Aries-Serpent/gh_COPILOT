"""WebSocket interface for quantum communication channels.

The production system exposes websocket endpoints for streaming quantum
results.  For testing purposes we emulate a very small portion of that
behaviour with an in-memory object that mimics the necessary attributes.
"""

from dataclasses import dataclass


@dataclass
class QuantumWebSocket:
    """Minimal representation of an opened websocket connection."""

    url: str
    messages: list[str] = None

    def __post_init__(self) -> None:  # pragma: no cover - trivial
        if self.messages is None:
            self.messages = []

    def send(self, message: str) -> None:
        """Store ``message`` in the internal buffer."""

        self.messages.append(message)

    def close(self) -> None:  # pragma: no cover - trivial
        """Close the websocket (no-op for the stub)."""


def open_quantum_socket(url: str) -> QuantumWebSocket:
    """Open a websocket connection to ``url``.

    The function performs basic validation to ensure a websocket URL is
    provided and returns a :class:`QuantumWebSocket` instance.
    """

    if not url.startswith("ws://") and not url.startswith("wss://"):
        raise ValueError("url must start with 'ws://' or 'wss://'")
    return QuantumWebSocket(url)


__all__ = ["QuantumWebSocket", "open_quantum_socket"]
