"""Pytest configuration for governance policy tests."""

from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Any, Dict

import pytest

try:  # pragma: no cover - optional dependency
    import yaml
except ImportError as exc:  # pragma: no cover
    raise ImportError("PyYAML is required for policy tests. Install PyYAML to proceed.") from exc

import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from analytics.analytics_db_inspector import record_governance_check

WAIVER_PATH = Path(__file__).with_name("waivers.yaml")


def _load_waivers() -> Dict[str, Dict[str, Any]]:
    if WAIVER_PATH.exists():
        with WAIVER_PATH.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or []
        return {w["check"]: w for w in data}
    return {}


WAIVERS = _load_waivers()


def pytest_runtest_setup(item: pytest.Item) -> None:
    waiver = WAIVERS.get(item.nodeid) or WAIVERS.get(item.name)
    if not waiver:
        return
    expires = dt.datetime.fromisoformat(waiver["expires"])
    if dt.datetime.utcnow() >= expires:
        return
    reason = waiver.get("reason", "waived policy check")
    action = waiver.get("action", "skip")
    if action == "xfail":
        pytest.xfail(reason)
    else:
        pytest.skip(reason)


def pytest_runtest_logreport(report: pytest.TestReport) -> None:
    if report.when != "call":
        return
    if report.failed:
        status = "failed"
    elif report.skipped:
        status = "skipped"
    elif getattr(report, "wasxfail", False):
        status = "xfail"
    else:
        status = "passed"
    record_governance_check(report.nodeid, status)
