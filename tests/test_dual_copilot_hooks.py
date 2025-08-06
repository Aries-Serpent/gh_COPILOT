from __future__ import annotations

import importlib
from unittest.mock import patch

import pytest


def test_code_placeholder_audit_hook(monkeypatch, tmp_path):
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    monkeypatch.setenv("GH_COPILOT_TEST_MODE", "1")
    monkeypatch.setenv("GH_COPILOT_DISABLE_VALIDATION", "1")
    module = importlib.reload(importlib.import_module("scripts.code_placeholder_audit"))
    with patch("scripts.code_placeholder_audit.DualCopilotOrchestrator") as orch_cls:
        instance = orch_cls.return_value
        instance.validator.validate_corrections.side_effect = RuntimeError("fail")
        with pytest.raises(RuntimeError):
            module.main(workspace_path=str(tmp_path))
        instance.validator.validate_corrections.assert_called_once()


def test_dashboard_updater_hook(monkeypatch, tmp_path):
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    module = importlib.reload(importlib.import_module("dashboard.compliance_metrics_updater"))
    with patch("dashboard.compliance_metrics_updater.DualCopilotOrchestrator") as orch_cls:
        inst = orch_cls.return_value
        inst.validator.validate_corrections.side_effect = RuntimeError("boom")
        with pytest.raises(RuntimeError):
            module.main(simulate=True, test_mode=True)
        inst.validator.validate_corrections.assert_called_once()


def test_autonomous_setup_and_audit_hook(monkeypatch, tmp_path):
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    monkeypatch.setenv("GH_COPILOT_DISABLE_VALIDATION", "1")
    monkeypatch.setenv("GH_COPILOT_TEST_MODE", "1")
    (tmp_path / "databases").mkdir()
    (tmp_path / "dashboard" / "compliance").mkdir(parents=True)
    module = importlib.reload(importlib.import_module("scripts.autonomous_setup_and_audit"))
    with patch("scripts.database.cross_database_sync_logger.log_sync_operation", lambda *a, **k: None):
        with patch("scripts.autonomous_setup_and_audit.DualCopilotOrchestrator") as orch_cls:
            inst = orch_cls.return_value
            inst.validator.validate_corrections.side_effect = RuntimeError("boom")
            with pytest.raises(RuntimeError):
                module.main()
            inst.validator.validate_corrections.assert_called_once()

