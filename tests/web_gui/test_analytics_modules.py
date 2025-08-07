from __future__ import annotations

from web_gui.analytics.user_behavior import log_user_action
from web_gui.analytics.performance_analysis import summarize_performance
from web_gui.analytics.pattern_recognition import find_repeated
from web_gui.analytics.predictive_models import predict_next

def test_log_user_action(monkeypatch) -> None:
    def fake_metrics() -> dict[str, float]:
        return {"cpu_percent": 1.0, "memory_percent": 2.0}

    monkeypatch.setattr(
        "web_gui.analytics.user_behavior.collect_performance_metrics",
        fake_metrics,
    )
    store, metrics = log_user_action("click")
    assert store["click"] == 1
    assert metrics["cpu_percent"] == 1.0

def test_summarize_performance(monkeypatch) -> None:
    def fake_metrics() -> dict[str, float]:
        return {"cpu_percent": 1.0, "memory_percent": 3.0}

    monkeypatch.setattr(
        "web_gui.analytics.performance_analysis.collect_performance_metrics",
        fake_metrics,
    )
    assert summarize_performance() == 2.0

def test_find_repeated() -> None:
    assert find_repeated([1, 2, 3, 1, 2, 4]) == [1, 2]

def test_predict_next(monkeypatch) -> None:
    def fake_metrics() -> dict[str, float]:
        return {"cpu_percent": 5.0, "memory_percent": 6.0}

    monkeypatch.setattr(
        "web_gui.analytics.predictive_models.collect_performance_metrics",
        fake_metrics,
    )
    assert predict_next() == 5.0
    assert predict_next([1.0, 2.0, 3.0]) == 4.0
