#!/usr/bin/env python3
from scripts.utilities.quantum_algorithm_library_expansion import EnterpriseUtility
import logging


def test_perform_utility_function_runs():
    util = EnterpriseUtility()
    assert util.perform_utility_function() is True
