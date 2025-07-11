import logging

from advanced_qubo_optimization import EnterpriseUtility


def test_qubo_optimization_logs(caplog):
    util = EnterpriseUtility(workspace_path=".")
    with caplog.at_level(logging.INFO):
        assert util.perform_utility_function()
    assert "Best solution" in caplog.text
