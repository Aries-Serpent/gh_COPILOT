"""WebSocket interface for quantum communication channels."""

from typing import Any, Dict


class QuantumWebSocket:
    """Very small WebSocket simulator for real-time interactions."""

    def __init__(self) -> None:
        self.connected = False

    def connect(self, url: str) -> None:
        """Pretend to establish a connection."""

        self.connected = True
        self.url = url

    def send(self, message: str) -> Dict[str, Any]:
        """Echo ``message`` back as a simulated response."""

        if not self.connected:  # pragma: no cover - defensive
            raise ConnectionError("WebSocket not connected")
        return {"url": self.url, "echo": message, "simulated": True}


def open_quantum_socket(url: str) -> QuantumWebSocket:
    """Return a connected :class:`QuantumWebSocket` instance."""

    ws = QuantumWebSocket()
    ws.connect(url)
    return ws
