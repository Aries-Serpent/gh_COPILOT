"""Verify orchestrators include dual-copilot validation hooks."""

from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]

ORCHESTRATOR_FILES = [
    "scripts/continuous_operation_orchestrator.py",
    "scripts/enterprise_deployment_orchestrator.py",
    "scripts/enterprise_validation_orchestrator.py",
    "scripts/enterprise_gh_copilot_deployment_orchestrator.py",
    "scripts/orchestrators/unified_wrapup_orchestrator.py",
]


@pytest.mark.parametrize("rel_path", ORCHESTRATOR_FILES)
def test_dual_copilot_invocation_present(rel_path: str) -> None:
    """Ensure each orchestrator references the secondary validator."""

    content = (ROOT / rel_path).read_text()
    assert "SecondaryCopilotValidator" in content
    assert "run_dual_copilot_validation" in content
    assert "validate_corrections" in content

