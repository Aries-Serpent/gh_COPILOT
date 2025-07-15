import logging
from pathlib import Path

from copilot.core.enterprise_orchestrator import EnterpriseUtility

logging.getLogger().setLevel(logging.CRITICAL)


def test_perform_utility_function_success(tmp_path):
    (tmp_path / "README.md").write_text("docs")
    util = EnterpriseUtility(workspace_path=str(tmp_path))
    assert util.perform_utility_function() is True


def test_perform_utility_function_failure(tmp_path):
    util = EnterpriseUtility(workspace_path=str(tmp_path))
    assert util.perform_utility_function() is False
