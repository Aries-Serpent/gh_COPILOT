"""High-level API for interacting with quantum services.

This module exposes a very small facade used throughout the tests to
simulate execution of quantum tasks.  The real project integrates with
various backends, but for unit testing we only need a deterministic and
side‑effect free implementation.  The :func:`execute_quantum_task` function
therefore wires together the template and websocket helpers defined in the
same package and returns a simple dictionary describing the result of the
operation.
"""

from typing import Any, Dict

from ghc_quantum.framework import QuantumExecutor
from ghc_quantum.framework.circuit import QuantumCircuit


def execute_quantum_task(task: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a quantum task using the simulation framework.

    Parameters
    ----------
    task:
        Dictionary describing the task.  Supported keys include ``"circuit"``
        whose value is a human-readable description of the circuit to run.

    Returns
    -------
    dict
        Dictionary containing the original task and a simulated execution
        result.
    """

    circuit = QuantumCircuit(str(task.get("circuit", "noop")))
    executor = QuantumExecutor()
    result = executor.run(circuit)
    return {"task": task, "result": result}
