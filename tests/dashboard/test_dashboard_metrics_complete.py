"""Comprehensive dashboard metric tests.

This module verifies that the live metrics stream exposes placeholder history
and that the dashboard template defines Chart.js gauges with descriptive
``title`` attributes.  The tests exercise server-sent events and basic HTML
parsing using lightweight string checks to avoid extra dependencies.
"""

from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path

import pytest

from dashboard import enterprise_dashboard as ed
from pathlib import Path


@pytest.fixture()
def app(tmp_path: Path, monkeypatch):
    """Provide a configured Flask application for dashboard tests."""

    metrics = tmp_path / "metrics.json"
    metrics.write_text(json.dumps({"metrics": {"lint_score": 90}}))

    db = tmp_path / "analytics.db"
    with sqlite3.connect(db) as conn:
        conn.execute(
            "CREATE TABLE placeholder_audit_snapshots (timestamp INTEGER, open_count INTEGER, resolved_count INTEGER)"
        )
        conn.execute(
            "INSERT INTO placeholder_audit_snapshots VALUES (1, 2, 1)"
        )

    monkeypatch.setattr(ed, "METRICS_FILE", metrics)
    monkeypatch.setattr(ed, "ANALYTICS_DB", db)
    return ed.app


def test_metrics_stream_includes_placeholder_history(app):
    """``/metrics_stream`` events should contain placeholder history data."""

    client = app.test_client()
    resp = client.get("/metrics_stream?once=1")
    assert resp.status_code == 200
    line = resp.data.decode().split("\n")[0]
    payload = json.loads(line.split("data: ")[1])
    assert payload["placeholder_history"][0]["open"] == 2


def test_dashboard_gauge_titles_and_chartjs():
    """Dashboard template defines gauges with titles and Chart.js helpers."""

    template = Path(ed.__file__).with_name("templates") / "dashboard.html"
    html = template.read_text()

    gauges = {
        "lintGauge": "Lint score gauge",
        "testGauge": "Test score gauge",
        "placeholderGauge": "Placeholder score gauge",
    }
    for gauge_id, title in gauges.items():
        pattern = rf'<canvas[^>]*id="{gauge_id}"[^>]*title="{title}"'
        assert re.search(pattern, html)

    # Ensure Chart.js gauge update helper is present.
    assert "function updateGauge(chart, value)" in html
    assert "new Chart(document.getElementById('lintGauge')" in html

