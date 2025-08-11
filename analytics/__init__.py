"""Analytics utilities package."""

from __future__ import annotations

from .pattern_recognition import detect_patterns, find_repeated
from .performance_analysis import calculate_throughput, summarize_performance
from .predictive_models import predict_next
from .user_behavior import log_user_action, track_active_users

__all__ = [
    "calculate_throughput",
    "detect_patterns",
    "find_repeated",
    "log_user_action",
    "predict_next",
    "summarize_performance",
    "track_active_users",
]

