"""Tests for quantum interface placeholders."""

import pytest

from quantum.interfaces import quantum_api, quantum_templates, quantum_websocket


def test_quantum_api_placeholder() -> None:
    with pytest.raises(NotImplementedError):
        quantum_api.execute_quantum_task({})


def test_quantum_templates_placeholder() -> None:
    with pytest.raises(NotImplementedError):
        quantum_templates.get_template("example")


def test_quantum_websocket_placeholder() -> None:
    with pytest.raises(NotImplementedError):
        quantum_websocket.open_quantum_socket("ws://example")
