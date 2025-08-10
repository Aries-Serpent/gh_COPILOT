import sqlite3
import sys
from types import SimpleNamespace

import secondary_copilot_validator


def test_single_snapshot_per_run(tmp_path, monkeypatch):
    workspace = tmp_path / "ws"
    workspace.mkdir()
    (workspace / "a.py").write_text("# TODO\n")

    analytics = tmp_path / "analytics.db"

    monkeypatch.setenv("GH_COPILOT_DISABLE_VALIDATION", "1")

    stub_validator = SimpleNamespace(
        DualCopilotOrchestrator=lambda: SimpleNamespace(
            validator=SimpleNamespace(validate_corrections=lambda *a, **k: True)
        )
    )
    sys.modules.setdefault(
        "scripts.validation.dual_copilot_orchestrator", stub_validator
    )
    sys.modules.setdefault(
        "dashboard.compliance_metrics_updater",
        SimpleNamespace(ComplianceMetricsUpdater=None),
    )
    sys.modules.setdefault(
        "unified_monitoring_optimization_system",
        SimpleNamespace(
            collect_metrics=lambda **_kwargs: {},
            push_metrics=lambda *a, **k: None,
            EnterpriseUtility=SimpleNamespace,
        ),
    )

    import scripts.code_placeholder_audit as audit

    monkeypatch.setattr(secondary_copilot_validator, "run_flake8", lambda *a, **k: True)
    monkeypatch.setattr(
        secondary_copilot_validator,
        "SecondaryCopilotValidator",
        lambda: SimpleNamespace(validate_corrections=lambda *a, **k: True),
    )
    monkeypatch.setattr(
        "scripts.code_placeholder_audit.ComplianceMetricsUpdater",
        lambda *a, **k: SimpleNamespace(update=lambda *a, **k: None, validate_update=lambda *a, **k: True),
    )
    audit._snapshot_recorded = False

    assert audit.main(workspace_path=str(workspace), analytics_db=str(analytics), production_db=None)

    with sqlite3.connect(analytics) as conn:
        cur = conn.execute("SELECT COUNT(*) FROM placeholder_audit_snapshots")
        assert cur.fetchone()[0] == 1
