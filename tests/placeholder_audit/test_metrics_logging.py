import json
import sqlite3
import sys
from pathlib import Path
from types import SimpleNamespace

import secondary_copilot_validator

stub_module = SimpleNamespace(
    DualCopilotOrchestrator=lambda: SimpleNamespace(
        validator=SimpleNamespace(validate_corrections=lambda *a, **k: True)
    )
)
sys.modules.setdefault(
    "scripts.validation.dual_copilot_orchestrator", stub_module
)


def _fake_collect_metrics(**_kwargs):
    return {"cpu_percent": 0.0}


def _fake_push_metrics(metrics, *, db_path=None, **_kwargs):
    path = Path(db_path)
    with sqlite3.connect(path) as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS monitoring_metrics (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, metrics_json TEXT NOT NULL)"
        )
        conn.execute(
            "INSERT INTO monitoring_metrics (metrics_json) VALUES (?)",
            (json.dumps(metrics),),
        )
        conn.commit()


sys.modules.setdefault(
    "unified_monitoring_optimization_system",
    SimpleNamespace(
        collect_metrics=_fake_collect_metrics,
        push_metrics=_fake_push_metrics,
        EnterpriseUtility=SimpleNamespace,
    ),
)

from scripts.code_placeholder_audit import main


def test_metrics_logged_and_dashboard_updated(tmp_path, monkeypatch):
    workspace = tmp_path / "ws"
    workspace.mkdir()
    (workspace / "a.py").write_text("# TODO\n")

    analytics = tmp_path / "analytics.db"
    dash_dir = tmp_path / "dashboard"

    monkeypatch.setenv("GH_COPILOT_DISABLE_VALIDATION", "1")
    monkeypatch.setattr(secondary_copilot_validator, "run_flake8", lambda *a, **k: True)
    monkeypatch.setattr(
        secondary_copilot_validator,
        "SecondaryCopilotValidator",
        lambda: SimpleNamespace(validate_corrections=lambda *a, **k: True),
    )
    monkeypatch.setattr(
        "scripts.code_placeholder_audit.ComplianceMetricsUpdater",
        lambda *a, **k: SimpleNamespace(
            update=lambda *a, **k: None, validate_update=lambda *a, **k: True
        ),
    )

    assert main(
        workspace_path=str(workspace),
        analytics_db=str(analytics),
        production_db=None,
        dashboard_dir=str(dash_dir / "compliance"),
    )

    metrics_file = dash_dir / "compliance" / "metrics.json"
    assert metrics_file.exists()
    metrics = json.loads(metrics_file.read_text())
    assert metrics["metrics"]["open_placeholders"] >= 1
    assert "progress" in metrics["metrics"]

    with sqlite3.connect(analytics) as conn:
        cur = conn.execute(
            "SELECT open_placeholders, resolved_placeholders FROM placeholder_metrics"
        )
        row = cur.fetchone()
        assert row[0] >= 1
        assert row[1] == 0
        cur = conn.execute(
            "SELECT metrics_json FROM monitoring_metrics ORDER BY id DESC LIMIT 1"
        )
        metrics_row = cur.fetchone()
        data = json.loads(metrics_row[0])
        assert data["placeholder_open"] >= 1
        assert data["placeholder_resolved"] == 0


def test_collect_metrics_called_for_findings(tmp_path, monkeypatch):
    workspace = tmp_path / "ws"
    workspace.mkdir()
    (workspace / "b.py").write_text("# TODO\n")

    analytics = tmp_path / "analytics.db"
    dash_dir = tmp_path / "dashboard"

    calls: list[dict] = []

    def _tracking_collect_metrics(**kwargs):
        calls.append(kwargs)
        return {"cpu_percent": 0.0}

    monkeypatch.setenv("GH_COPILOT_DISABLE_VALIDATION", "1")
    monkeypatch.setattr(secondary_copilot_validator, "run_flake8", lambda *a, **k: True)
    monkeypatch.setattr(
        secondary_copilot_validator,
        "SecondaryCopilotValidator",
        lambda: SimpleNamespace(validate_corrections=lambda *a, **k: True),
    )
    monkeypatch.setattr(
        "scripts.code_placeholder_audit.ComplianceMetricsUpdater",
        lambda *a, **k: SimpleNamespace(
            update=lambda *a, **k: None, validate_update=lambda *a, **k: True
        ),
    )
    monkeypatch.setattr("scripts.code_placeholder_audit.collect_metrics", _tracking_collect_metrics)
    monkeypatch.setattr("scripts.code_placeholder_audit.push_metrics", _fake_push_metrics)

    assert main(
        workspace_path=str(workspace),
        analytics_db=str(analytics),
        production_db=None,
        dashboard_dir=str(dash_dir / "compliance"),
    )

    assert len(calls) == 2
