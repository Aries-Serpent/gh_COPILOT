import importlib.util
from pathlib import Path

import pytest


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "enterprise_compliance_monitor.py"
spec = importlib.util.spec_from_file_location("ecm", MODULE_PATH)
ecm = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(ecm)  # type: ignore[union-attr]


def test_monitor_aborts_when_validator_missing(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(ecm, "DualCopilotValidator", None)
    monkeypatch.setattr(ecm, "DUAL_COPILOT_IMPORT_ERROR", ImportError("missing"))
    monitor = ecm.EnterpriseComplianceMonitor(workspace_path=str(tmp_path))
    with pytest.raises(RuntimeError):
        monitor.start_compliance_monitoring()


def test_monitor_raises_on_validator_failure(monkeypatch, tmp_path: Path) -> None:
    class FailingValidator:
        def validate_execution(self):  # pragma: no cover - simple stub
            class Result:
                passed = False
                errors = ["boom"]

            return Result()

    monkeypatch.setattr(ecm, "DualCopilotValidator", FailingValidator)
    monitor = ecm.EnterpriseComplianceMonitor(workspace_path=str(tmp_path))
    with pytest.raises(RuntimeError):
        monitor.start_compliance_monitoring()

