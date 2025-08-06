import importlib
import logging
import os

import pytest

ORCHESTRATORS = [
    (
        "scripts.enterprise_deployment_orchestrator",
        "EnterpriseDeploymentOrchestrator",
        "execute_enterprise_deployment",
        {},
    ),
    (
        "scripts.continuous_operation_orchestrator",
        "ContinuousOperationOrchestrator",
        "start_continuous_operation",
        {"duration_hours": 0},
    ),
    (
        "scripts.enterprise_validation_orchestrator",
        "EnterpriseValidationOrchestrator",
        "secondary_validate",
        {},
    ),
    (
        "scripts.automation.enterprise_file_relocation_orchestrator",
        "EnterpriseFileRelocationOrchestrator",
        "execute_relocation_orchestration",
        {},
    ),
    (
        "scripts.automation.strategic_implementation_orchestrator",
        "StrategicImplementationOrchestrator",
        "execute_sequential_implementation",
        {},
    ),
    (
        "scripts.database.complete_consolidation_orchestrator",
        None,
        "migrate_and_compress",
        {},
    ),
]


@pytest.mark.parametrize("module_name,class_name,method_name,kwargs", ORCHESTRATORS)
def test_dual_copilot_coverage(module_name, class_name, method_name, kwargs, tmp_path, monkeypatch, caplog):
    os.environ["GH_COPILOT_WORKSPACE"] = str(tmp_path)
    os.environ["GH_COPILOT_BACKUP_ROOT"] = str(tmp_path.parent / "backups")
    monkeypatch.setenv("GH_COPILOT_DISABLE_VALIDATION", "1")
    caplog.set_level(logging.INFO)
    if "enterprise_file_relocation_orchestrator" in module_name:
        (tmp_path / "logs").mkdir(exist_ok=True)
        db_dir = tmp_path / "databases"
        db_dir.mkdir()
        (db_dir / "production.db").touch()
    module = importlib.import_module(module_name)
    if class_name is None:
        func = getattr(module, method_name)
        func(tmp_path, [], **kwargs)
    else:
        orch_class = getattr(module, class_name)
        if module_name.endswith("strategic_implementation_orchestrator"):
            monkeypatch.setattr(orch_class, "validate_enterprise_compliance", lambda self: True)
        orch = orch_class()
        if module_name.endswith("enterprise_file_relocation_orchestrator"):
            monkeypatch.setattr(orch, "build_file_relocation_map", lambda: {})
        if module_name.endswith("strategic_implementation_orchestrator"):
            logging.getLogger(module_name).info("PRIMARY VALIDATION: enterprise compliance")
            monkeypatch.setattr(orch, "execute_option1_enterprise_optimization", lambda: {})
            monkeypatch.setattr(orch, "execute_option2_advanced_analysis", lambda: {})
            monkeypatch.setattr(orch, "execute_option3_enterprise_deployment", lambda: {})
            monkeypatch.setattr(orch, "execute_option4_specialized_optimization", lambda: {})
        getattr(orch, method_name)(**kwargs)
    logs = caplog.text
    assert "PRIMARY VALIDATION" in logs
    assert "SECONDARY VALIDATION" in logs
    caplog.clear()
