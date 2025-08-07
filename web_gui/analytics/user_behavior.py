"""User behavior analytics for the web GUI."""

from __future__ import annotations

from typing import Dict, Sequence, Tuple

from web_gui.monitoring.performance_metrics import collect_performance_metrics

__all__ = ["log_user_action", "UserBehaviorModel"]


def log_user_action(action: str, storage: Dict[str, int] | None = None) -> Tuple[Dict[str, int], Dict[str, float]]:
    """Record an ``action`` and capture current performance metrics."""
    store = storage if storage is not None else {}
    store[action] = store.get(action, 0) + 1
    metrics = collect_performance_metrics()
    return store, metrics


class UserBehaviorModel:
    """Stub model for user behavior prediction."""

    def predict(self, actions: Sequence[str]) -> str:
        """Return the most recent action or an empty string."""
        return actions[-1] if actions else ""
