from quantum.quantum_optimization import EnterpriseUtility


def test_execute_utility_returns_true():
    util = EnterpriseUtility()
    assert util.execute_utility() is True
