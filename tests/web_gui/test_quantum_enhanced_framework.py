"""Tests for :mod:`web_gui.scripts.flask_apps.quantum_enhanced_framework`."""

from __future__ import annotations

import importlib

import pytest


def test_available_algorithms() -> None:
    """Framework should expose algorithm listing when quantum modules exist."""

    from web_gui.scripts.flask_apps.quantum_enhanced_framework import (
        QuantumEnhancedFramework,
    )

    framework = QuantumEnhancedFramework()
    algorithms = framework.available_algorithms()
    assert isinstance(algorithms, list)


def test_fallback_when_quantum_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    """Import errors should trigger classical fallback pathways."""

    from web_gui.scripts.flask_apps import quantum_enhanced_framework as qef_module

    def fake_import(name: str, *args, **kwargs):  # pragma: no cover - simulated
        raise ImportError("missing quantum libs")

    monkeypatch.setattr(importlib, "import_module", fake_import)

    framework = qef_module.QuantumEnhancedFramework()
    result = framework.run_algorithm("does_not_matter")
    assert result["status"] == "unavailable"
    scored = framework.score_templates(["a", "b"], tag="x")
    assert scored == [("a", 1.0), ("b", 1.0)]


def test_blueprint_endpoints(monkeypatch: pytest.MonkeyPatch) -> None:
    from flask import Flask
    from web_gui.scripts.flask_apps import quantum_enhanced_framework as qef

    app = Flask(__name__)
    app.register_blueprint(qef.quantum_bp, url_prefix="/quantum")

    monkeypatch.setattr(qef.framework, "available_algorithms", lambda: ["demo"])
    client = app.test_client()
    resp = client.get("/quantum/algorithms")
    assert resp.get_json()["algorithms"] == ["demo"]

    monkeypatch.setattr(
        qef.framework,
        "run_algorithm",
        lambda name, **kw: {"status": "ok", "name": name},
    )
    resp = client.post("/quantum/run/test", json={})
    assert resp.get_json()["status"] == "ok"

    monkeypatch.setattr(
        qef.framework,
        "score_templates",
        lambda templates, tag: [(templates[0], 1.0)],
    )
    resp = client.post("/quantum/score", json={"templates": ["t"], "tag": "x"})
    assert resp.get_json()["scores"] == [["t", 1.0]]

