"""Tests for quantum placeholder modules."""

import importlib
import sys

import pytest


def _import_placeholder():
    """Import placeholder algorithm with fresh modules."""
    sys.modules.pop("scripts.quantum_placeholders", None)
    sys.modules.pop("scripts.quantum_placeholders.quantum_placeholder_algorithm", None)
    return importlib.import_module(
        "scripts.quantum_placeholders.quantum_placeholder_algorithm"
    )


def test_simulate_quantum_process_round_trip(monkeypatch):
    monkeypatch.delenv("GH_COPILOT_ENV", raising=False)
    module = _import_placeholder()
    data = [1, 2, 3]
    assert module.simulate_quantum_process(data) == data


def test_placeholder_raises_in_production(monkeypatch):
    monkeypatch.setenv("GH_COPILOT_ENV", "production")
    with pytest.raises(RuntimeError, match="should not be used in production"):
        module = _import_placeholder()
        module.simulate_quantum_process([1])


def test_module_import_disallowed_in_production(monkeypatch):
    monkeypatch.setenv("GH_COPILOT_ENV", "production")
    sys.modules.pop("scripts.quantum_placeholders", None)
    with pytest.raises(RuntimeError, match="should not be used in production"):
        importlib.import_module("scripts.quantum_placeholders")

