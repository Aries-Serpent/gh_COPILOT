import pytest

pytest.importorskip("qiskit")
pytest.importorskip("numpy")

from ghc_quantum.integration import QuantumSecureChannel


def test_round_trip_default_key():
    channel = QuantumSecureChannel()
    message = "hello quantum"
    assert channel.transmit(message) == message


def test_round_trip_custom_key():
    channel = QuantumSecureChannel(key="custom")
    message = "secret message"
    assert channel.transmit(message) == message


def test_round_trip_empty_payload():
    channel = QuantumSecureChannel()
    assert channel.transmit("") == ""
