"""Regression tests for quantum hardware hooks.

These hooks are generated to provide lightweight interfaces for various
quantum providers. The tests ensure that the public API for each hook is
stable and always exposes a predictable set of keys, even when optional
dependencies are missing or misconfigured.
"""

from __future__ import annotations

import importlib
from typing import Dict

import pytest


@pytest.mark.parametrize(
    "module_name,value_key",
    [
        ("hardware_hooks.qiskit", "counts"),
        ("hardware_hooks.ionq", "counts"),
        ("hardware_hooks.dwave", "record"),
    ],
)
def test_run_sample_circuit_keys(module_name: str, value_key: str) -> None:
    """`run_sample_circuit` should always provide core keys.

    The function returns a dictionary describing the execution result. In
    earlier revisions, some keys were omitted when a backend was
    unavailable, causing ``KeyError`` in downstream consumers. The
    regression check verifies that ``status``, ``backend`` and the
    backend-specific result key are always present.
    """

    module = importlib.import_module(module_name)
    result: Dict[str, object] = module.run_sample_circuit()

    # Access the keys directly to ensure they exist without raising errors.
    assert "status" in result
    assert "backend" in result
    assert value_key in result

    # Bonus: attempt to access them. Any missing key would raise KeyError.
    _ = result["status"]
    _ = result["backend"]
    _ = result[value_key]

