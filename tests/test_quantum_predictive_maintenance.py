import logging

from quantum_neural_networks_predictive_maintenance import EnterpriseUtility


def test_qnn_predictive_maintenance_accuracy(caplog):
    util = EnterpriseUtility()
    with caplog.at_level(logging.INFO):
        result = util.perform_utility_function()
    assert result is True

    for record in caplog.records:
        msg = record.getMessage()
        if "Accuracy:" in msg:
            accuracy = float(msg.split("Accuracy:")[1])
            assert accuracy > 0.5
            break
    else:
        raise AssertionError("Accuracy log not found")
