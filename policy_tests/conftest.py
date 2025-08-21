"""Pytest configuration for governance policy tests."""

from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Any, Dict

import pytest

yaml = pytest.importorskip(
    "yaml", reason="Requires PyYAML; install with `pip install pyyaml`."
)

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
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=dt.timezone.utc)
    if dt.datetime.now(dt.timezone.utc) >= expires:
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
