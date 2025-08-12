"""Tests for quantum interface simulation placeholders."""
from ghc_quantum.interfaces import quantum_api, quantum_templates, quantum_websocket


def test_quantum_api_simulation() -> None:
    result = quantum_api.execute_quantum_task({"circuit": "demo"})
    assert result["result"]["simulated"] is True


def test_quantum_templates_simulation() -> None:
    assert quantum_templates.get_template("bell_pair").startswith("placeholder")


def test_quantum_websocket_simulation() -> None:
    ws = quantum_websocket.open_quantum_socket("ws://example")
    assert ws.send("hi") == {"url": "ws://example", "echo": "hi", "simulated": True}
