"""High-level API for interacting with quantum services."""

from typing import Any, Dict

from quantum.framework import QuantumExecutor
from quantum.framework.circuit import QuantumCircuit


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
