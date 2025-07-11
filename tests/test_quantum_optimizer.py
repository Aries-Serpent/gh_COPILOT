import logging

from quantum.quantum_optimization import EnterpriseUtility


def test_gradient_descent_logs(caplog):
    util = EnterpriseUtility(workspace_path=".")
    with caplog.at_level(logging.INFO):
        assert util.perform_utility_function()
    assert "Optimized value" in caplog.text
