import logging
import importlib
import os
from scripts.enterprise_validation_orchestrator import ValidationMetrics


def _dummy_metrics():
    return ValidationMetrics(
        validation_id="t",
        total_scripts=0,
        validated_scripts=0,
        passed_scripts=0,
        failed_scripts=0,
        critical_issues=0,
        performance_issues=0,
        security_issues=0,
        integration_issues=0,
        database_issues=0,
        overall_score=100.0,
        validation_duration=0.0,
        system_health_score=1.0,
        enterprise_compliance_score=1.0,
        optimization_recommendations=[],
        critical_actions_required=[],
    )


def _instantiate(module_name: str, cls_name: str):
    os.environ["GH_COPILOT_DISABLE_VALIDATION"] = "1"
    mod = importlib.import_module(module_name)
    cls = getattr(mod, cls_name)
    obj = cls()
    if module_name.endswith("enterprise_validation_orchestrator"):
        obj.validation_metrics = _dummy_metrics()
    return obj


def test_dual_copilot_coverage(caplog):
    caplog.set_level(logging.INFO)

    modules = [
        ("scripts.enterprise_deployment_orchestrator", "EnterpriseDeploymentOrchestrator"),
        ("scripts.enterprise_gh_copilot_deployment_orchestrator", "EnterpriseUtility"),
        ("scripts.regenerated.integrated_deployment_orchestrator", "EnterpriseUtility"),
        ("scripts.continuous_operation_orchestrator", "ContinuousOperationOrchestrator"),
        ("scripts.automation.enterprise_file_relocation_orchestrator", "EnterpriseFileRelocationOrchestrator"),
        ("scripts.automation.ml_training_pipeline_orchestrator", "MLPipelineOrchestrator"),
        ("scripts.automation.quantum_integration_orchestrator", "EnterpriseUtility"),
        ("scripts.automation.strategic_implementation_orchestrator", "StrategicImplementationOrchestrator"),
        ("scripts.orchestrators.unified_wrapup_orchestrator", "UnifiedWrapUpOrchestrator"),
        ("scripts.enterprise_validation_orchestrator", "EnterpriseValidationOrchestrator"),
    ]

    for mod_name, cls_name in modules:
        obj = _instantiate(mod_name, cls_name)
        if hasattr(obj, "primary_validate"):
            obj.primary_validate()
        if hasattr(obj, "secondary_validate"):
            obj.secondary_validate()

    cc = importlib.import_module("scripts.database.complete_consolidation_orchestrator")
    cc.primary_validate()
    cc.secondary_validate()

    assert "PRIMARY" in caplog.text
    assert "SECONDARY" in caplog.text
