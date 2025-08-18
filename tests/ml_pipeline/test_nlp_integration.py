"""Integration tests for :mod:`ai_enhancement.nlp`."""

import time

from ai_enhancement.nlp import process_text


def test_process_text_flow(monkeypatch):
    captured = {}

    def fake_send(event, payload):  # pragma: no cover - simple capture
        captured["event"] = event
        captured["payload"] = payload

    monkeypatch.setattr("ai_enhancement.nlp._send_to_gui", fake_send)
    result = process_text("hello")
    assert result == {"processed": "HELLO", "simulated": True}
    assert captured["event"] == "nlp"
    assert captured["payload"] == result


def test_process_text_benchmark(monkeypatch, benchmark):
    monkeypatch.setattr("ai_enhancement.nlp._send_to_gui", lambda *a, **k: None)
    start = time.perf_counter()
    result = process_text("benchmark")
    assert time.perf_counter() - start < 0.1
    assert result["processed"] == "BENCHMARK"
    assert result["simulated"] is True
    benchmark(process_text, "benchmark")
