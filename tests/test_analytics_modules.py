from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from analytics import (
    calculate_throughput,
    detect_patterns,
    predict_next,
    track_active_users,
)


def test_track_active_users():
    assert track_active_users(["a", "b", "a"]) == 2


def test_calculate_throughput():
    assert calculate_throughput(100, 10) == 10


def test_detect_patterns():
    assert detect_patterns([1, 1, 2]) == {1: 2, 2: 1}


def test_predict_next():
    assert predict_next([1.0, 2.0, 3.0]) == 4.0
