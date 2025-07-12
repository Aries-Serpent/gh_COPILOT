from quantum_algorithm_library_expansion import EnterpriseUtility


def test_perform_utility_function_runs():
    util = EnterpriseUtility()
    assert util.perform_utility_function() is True
