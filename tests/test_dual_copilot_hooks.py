from __future__ import annotations

import importlib
from unittest.mock import patch

import pytest


def test_simple_placeholder_audit_hook(tmp_path):
    (tmp_path / "f.txt").write_text("TODO\n")
    module = importlib.reload(importlib.import_module("scripts.simple_placeholder_audit"))
    with patch("scripts.simple_placeholder_audit.SecondaryCopilotValidator") as sec_cls, patch(
        "scripts.simple_placeholder_audit.DualCopilotOrchestrator"
    ) as orch_cls:
        sec_cls.return_value.validate_corrections.return_value = True
        inst = orch_cls.return_value
        inst.validator.validate_corrections.side_effect = RuntimeError("fail")
        with pytest.raises(RuntimeError):
            module.main(
                [
                    str(tmp_path),
                    "--analytics-db",
                    str(tmp_path / "a.db"),
                    "--production-db",
                    str(tmp_path / "p.db"),
                ]
            )
        inst.validator.validate_corrections.assert_called_once()


def test_dashboard_updater_hook(monkeypatch, tmp_path):
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    module = importlib.reload(importlib.import_module("dashboard.compliance_metrics_updater"))
    with patch("dashboard.compliance_metrics_updater.DualCopilotOrchestrator") as orch_cls:
        inst = orch_cls.return_value
        inst.validator.validate_corrections.side_effect = RuntimeError("boom")
        with pytest.raises(RuntimeError):
            module.main(simulate=True, test_mode=True)
        inst.validator.validate_corrections.assert_called_once()


def test_template_asset_ingestor_hook(monkeypatch, tmp_path):
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    (tmp_path / "databases").mkdir()
    tmpl_dir = tmp_path / "prompts"
    tmpl_dir.mkdir()
    (tmpl_dir / "t.md").write_text("hello")
    module = importlib.reload(importlib.import_module("scripts.database.template_asset_ingestor"))
    with patch("scripts.database.template_asset_ingestor.validate_enterprise_operation", lambda *a, **k: None), patch(
        "scripts.database.template_asset_ingestor.get_dataset_sources", return_value=[]
    ), patch("scripts.database.template_asset_ingestor.get_lesson_templates", return_value={}), patch(
        "scripts.database.template_asset_ingestor.log_sync_operation", lambda *a, **k: None
    ), patch("scripts.database.template_asset_ingestor.check_database_sizes", return_value=True), patch(
        "scripts.database.template_asset_ingestor.DualCopilotOrchestrator"
    ) as orch_cls:
        inst = orch_cls.return_value
        inst.validator.validate_corrections.side_effect = RuntimeError("boom")
        with pytest.raises(RuntimeError):
            module.ingest_templates(tmp_path, tmpl_dir)
        inst.validator.validate_corrections.assert_called_once()
