"""Quantum performance benchmark tests."""

from scripts.validation.quantum_performance_integration_tester import (
    EnterpriseUtility,
)


def test_quantum_benchmark_runs() -> None:
    """The benchmark utility should successfully run a small circuit."""
    util = EnterpriseUtility()
    assert util.perform_utility_function()

