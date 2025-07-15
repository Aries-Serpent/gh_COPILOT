#!/usr/bin/env python3
import logging

import pytest

pytest.importorskip("qiskit_machine_learning")

try:
    from quantum_neural_networks_predictive_maintenance import (
        EnterpriseUtility,
        EstimatorQNN as ModuleEstimatorQNN,
    )
except Exception as exc:  # pragma: no cover - skip if dependencies missing
    EnterpriseUtility = None
    ModuleEstimatorQNN = None
    SKIP_REASON = str(exc)
else:
    SKIP_REASON = ""


def test_qnn_predictive_maintenance_accuracy(caplog):
    if EnterpriseUtility is None:
        pytest.skip(SKIP_REASON)
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


def test_predictive_maintenance_uses_estimator_qnn():
    if ModuleEstimatorQNN is None:
        pytest.skip(SKIP_REASON)
    from qiskit_machine_learning.neural_networks import EstimatorQNN

    assert ModuleEstimatorQNN is EstimatorQNN
