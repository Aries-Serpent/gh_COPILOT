from analytics.user_behavior import track_active_users
from analytics.performance_analysis import calculate_throughput
from analytics.pattern_recognition import detect_patterns
from analytics.predictive_models import predict_next


def test_track_active_users():
    assert track_active_users(["a", "b", "a"]) == 2


def test_calculate_throughput():
    assert calculate_throughput(100, 10) == 10


def test_detect_patterns():
    assert detect_patterns([1, 1, 2]) == {1: 2, 2: 1}


def test_predict_next():
    assert predict_next([1.0, 2.0, 3.0]) == 2.0
