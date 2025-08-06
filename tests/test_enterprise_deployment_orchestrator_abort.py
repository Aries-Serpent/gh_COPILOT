import pytest

from enterprise_modules import compliance
from scripts import enterprise_deployment_orchestrator as edo


def test_execute_enterprise_deployment_aborts_on_validation_failure(monkeypatch, tmp_path):
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(tmp_path.parent / "backups"))
    monkeypatch.setattr(compliance, "validate_enterprise_operation", lambda: True)
    monkeypatch.setattr(edo.SecondaryCopilotValidator, "validate_corrections", lambda self, _files: True)
    monkeypatch.setattr(edo.EnterpriseDeploymentOrchestrator, "secondary_validate", lambda self: True)

    for method in [
        "_execute_pre_deployment_validation",
        "_deploy_core_systems",
        "_deploy_database_systems",
        "_deploy_integration_systems",
        "_deploy_security_systems",
        "_deploy_monitoring_systems",
        "_execute_post_deployment_validation",
    ]:
        monkeypatch.setattr(edo.EnterpriseDeploymentOrchestrator, method, lambda self: {"status": "COMPLETED", "score": 100})

    def fake_run_dual(primary, secondary):
        primary()
        secondary()
        return False

    monkeypatch.setattr(edo, "run_dual_copilot_validation", fake_run_dual)

    orchestrator = edo.EnterpriseDeploymentOrchestrator(str(tmp_path))
    with pytest.raises(RuntimeError):
        orchestrator.execute_enterprise_deployment()
