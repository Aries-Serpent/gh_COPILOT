import secondary_copilot_validator
from scripts.validation.enterprise_dual_copilot_validator import (
    EnterpriseOrchestrator,
    EnterpriseSystemConfig,
)


def test_enterprise_orchestrator_triggers_secondary_validation(monkeypatch):
    orchestrator = EnterpriseOrchestrator(EnterpriseSystemConfig())

    monkeypatch.setattr(
        orchestrator.primary_copilot,
        "execute_enterprise_flake8_correction",
        lambda target: {"phase": {"file_list": ["foo.py"]}},
    )

    called = {}

    def fake_run(files):
        called["files"] = list(files)
        return True

    monkeypatch.setattr(secondary_copilot_validator, "run_flake8", fake_run)
    monkeypatch.setattr(
        orchestrator.secondary_copilot,
        "validate_primary_execution",
        lambda primary, metrics: type(
            "R",
            (),
            {
                "primary_execution_success": True,
                "secondary_validation_passed": True,
                "enterprise_standards_met": True,
                "overall_compliance_score": 1.0,
                "recommendations": [],
            },
        )(),
    )

    orchestrator.execute_enterprise_flake8_system(".")

    assert called.get("files") == ["foo.py"]
