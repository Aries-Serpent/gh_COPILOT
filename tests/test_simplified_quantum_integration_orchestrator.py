#!/usr/bin/env python3
from archive.consolidated_scripts.simplified_quantum_integration_orchestrator import EnterpriseUtility
from simplified_quantum_integration_orchestrator import hello_world


def test_perform_utility_function_runs():
    util = EnterpriseUtility()
    assert util.perform_utility_function() is True


def test_hello_world_output(capsys):
    hello_world()
    captured = capsys.readouterr()
    assert "Hello, world!" in captured.out
