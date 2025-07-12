from expanded_quantum_algorithm_library import EnterpriseUtility


def test_perform_utility_function_runs():
    util = EnterpriseUtility()
    assert util.perform_utility_function() is True
