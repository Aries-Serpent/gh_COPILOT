#!/usr/bin/env python3
from quantum.quantum_optimization import EnterpriseUtility
import logging


def test_perform_utility_function_converges():
    util = EnterpriseUtility()
    assert util.perform_utility_function() is True
