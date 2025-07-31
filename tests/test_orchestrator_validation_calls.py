import importlib

import pytest

from enterprise_modules import compliance


@pytest.mark.parametrize(
    "module_name,class_name,method_name",
    [
        (
            "scripts.enterprise_deployment_orchestrator",
            "EnterpriseDeploymentOrchestrator",
            "execute_enterprise_deployment",
        ),
        ("scripts.enterprise_validation_orchestrator", "EnterpriseValidationOrchestrator", None),
        ("scripts.orchestrators.unified_wrapup_orchestrator", "UnifiedWrapUpOrchestrator", None),
    ],
)
def test_orchestrators_call_validate(monkeypatch, tmp_path, module_name, class_name, method_name):
    calls = []

    def fake_validate(*_a, **_k):
        calls.append(True)
        return True

    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(tmp_path.parent / "backups"))
    monkeypatch.setattr(compliance, "validate_enterprise_operation", fake_validate)

    module = importlib.import_module(module_name)
    cls = getattr(module, class_name)

    if method_name is None:
        cls(str(tmp_path))
        assert calls
    else:
        # patch heavy operations
        if module_name.endswith("enterprise_deployment_orchestrator"):
            monkeypatch.setattr(cls, "_execute_pre_deployment_validation", lambda self: {"status": "OK", "score": 100})
            monkeypatch.setattr(cls, "_deploy_core_systems", lambda self: {"status": "OK", "score": 100})
            monkeypatch.setattr(cls, "_deploy_database_systems", lambda self: {"status": "OK", "score": 100})
            monkeypatch.setattr(cls, "_deploy_integration_systems", lambda self: {"status": "OK", "score": 100})
            monkeypatch.setattr(cls, "_deploy_security_systems", lambda self: {"status": "OK", "score": 100})
            monkeypatch.setattr(cls, "_deploy_monitoring_systems", lambda self: {"status": "OK", "score": 100})
            monkeypatch.setattr(cls, "_execute_post_deployment_validation", lambda self: {"status": "OK", "score": 100})
            monkeypatch.setattr(cls, "_log_deployment_summary", lambda self, *_a, **_k: None)
        obj = cls(str(tmp_path))
        assert calls
        calls.clear()
        getattr(obj, method_name)()
        assert calls
