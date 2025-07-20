import json
from scripts.utilities.PHASE3_IMPLEMENTATION_STRATEGY import EnterpriseUtility


def test_phase3_utility_creates_summary(tmp_path):
    (tmp_path / "config").mkdir()
    (tmp_path / "misc").mkdir()
    with open(tmp_path / "config" / "phase3.json", "w", encoding="utf-8") as f:
        json.dump({"value": 1}, f)

    util = EnterpriseUtility(workspace_path=str(tmp_path))
    assert util.perform_utility_function() is True

    result = tmp_path / "results" / "phase3_summary.json"
    assert result.exists()
    data = json.load(open(result, "r", encoding="utf-8"))
    assert data["config_present"] is True
