"""Command line demo for the :mod:`monitoring` package."""

from __future__ import annotations

from typing import Any, Dict

from .collector import collect_and_detect


def _demo_source() -> Dict[str, Any]:
    """Return static metrics used for the demo."""

    return {"uptime": 12345, "cpu": 0.15}


def _demo_detector(metrics: Dict[str, Any]) -> Dict[str, Any]:
    """Flag when CPU usage exceeds 90% in the demo metrics."""

    m = metrics.get("demo", {})
    return {"detector": "demo", "flag": m.get("cpu", 0) > 0.9}


if __name__ == "__main__":
    result = collect_and_detect({"demo": _demo_source}, [_demo_detector])
    print(result)
