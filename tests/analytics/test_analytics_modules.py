from analytics.user_behavior import log_user_action
from analytics.performance_analysis import summarize_performance
from analytics.pattern_recognition import find_repeated
from analytics.predictive_models import predict_next


def test_log_user_action() -> None:
    store = log_user_action("click")
    assert store["click"] == 1
    store = log_user_action("click", store)
    assert store["click"] == 2


def test_summarize_performance() -> None:
    assert summarize_performance({"a": 1.0, "b": 3.0}) == 2.0


def test_find_repeated() -> None:
    assert find_repeated([1, 2, 3, 1, 2, 4]) == [1, 2]


def test_predict_next() -> None:
    assert predict_next([1.0, 2.0, 3.0]) == 4.0
