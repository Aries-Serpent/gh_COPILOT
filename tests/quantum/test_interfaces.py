"""Tests for the quantum interface layer."""

from quantum.interfaces import quantum_api, quantum_templates, quantum_websocket


def test_execute_quantum_task() -> None:
    result = quantum_api.execute_quantum_task({"template": "increment", "input": 3})
    assert result["result"] == 4


def test_get_template_and_apply() -> None:
    tmpl = quantum_templates.get_template("double")
    assert tmpl(5) == 10


def test_open_quantum_socket() -> None:
    socket = quantum_websocket.open_quantum_socket("ws://example")
    assert socket.url == "ws://example"
