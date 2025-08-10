"""Tests for ComplianceValidator, CorrectionEngine, and ComplianceDashboard."""

from scripts.enterprise_compliance_monitor import (
    ComplianceValidator,
    CorrectionEngine,
    ComplianceDashboard,
    ComplianceResult,
    ComplianceLevel,
    ComplianceCategory,
    CorrectionType,
    EnterpriseComplianceMonitor,
    ComplianceConfiguration,
)


def test_compliance_components_integration(tmp_path):
    """Validator, correction engine and dashboard integrate with monitor."""
    config = ComplianceConfiguration(compliance_threshold=80.0)
    monitor = EnterpriseComplianceMonitor(workspace_path=tmp_path, config=config)

    result = ComplianceResult(
        category=ComplianceCategory.CODE_QUALITY,
        score=50.0,
        level=ComplianceLevel.CRITICAL,
        description="test",
        details={},
        violations=["low score"],
        recommendations=[],
        correction_type=CorrectionType.AUTOMATIC,
        timestamp="now",
        validation_id="1",
    )

    validator = ComplianceValidator(80.0)
    assert not validator.is_compliant(result)

    engine = CorrectionEngine()
    corrected = engine.apply(result)
    assert corrected.score == 100.0

    dashboard = ComplianceDashboard()
    overview = dashboard.generate_overview(monitor.compliance_metrics)
    assert overview["overall_score"] == monitor.compliance_metrics.overall_score
    # monitor exposes these components as attributes
    assert isinstance(monitor.validator, ComplianceValidator)
    assert isinstance(monitor.correction_engine, CorrectionEngine)
    assert isinstance(monitor.dashboard, ComplianceDashboard)
