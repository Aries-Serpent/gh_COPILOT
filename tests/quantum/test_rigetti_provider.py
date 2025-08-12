"""Tests for the :mod:`quantum.providers.rigetti_provider` module."""

import pytest

pytest.importorskip("pyquil")

from quantum.framework.backend import QuantumBackend
from quantum.providers.rigetti_provider import RigettiProvider


def test_rigetti_provider_unavailable_without_env(monkeypatch):
    monkeypatch.delenv("RIGETTI_API_KEY", raising=False)
    monkeypatch.delenv("RIGETTI_CLUSTER_URL", raising=False)
    provider = RigettiProvider()
    assert provider.is_available() is False


def test_rigetti_provider_backend(monkeypatch):
    monkeypatch.setenv("RIGETTI_API_KEY", "dummy")
    monkeypatch.setenv("RIGETTI_CLUSTER_URL", "http://example.com")
    provider = RigettiProvider()
    assert provider.is_available()
    backend = provider.get_backend()
    assert isinstance(backend, QuantumBackend)

