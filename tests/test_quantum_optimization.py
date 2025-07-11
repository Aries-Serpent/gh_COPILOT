from quantum.quantum_optimization import EnterpriseUtility


def test_perform_utility_function_converges():
    util = EnterpriseUtility()
    assert util.perform_utility_function() is True
