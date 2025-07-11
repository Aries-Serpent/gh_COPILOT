from quantum.quantum_optimization import EnterpriseUtility


def test_perform_utility_function():
    util = EnterpriseUtility()
    assert util.perform_utility_function() is True
