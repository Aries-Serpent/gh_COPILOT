import json
from scripts.deployment.strategic_implementation_executor import EnterpriseUtility


def test_executor_creates_summary(tmp_path):
    (tmp_path / "misc").mkdir()
    util = EnterpriseUtility(workspace_path=str(tmp_path))
    assert util.perform_utility_function() is True

    result = tmp_path / "results" / "strategic_executor_summary.json"
    assert result.exists()
    data = json.load(open(result, "r", encoding="utf-8"))
    assert data["workspace"] == str(tmp_path)
