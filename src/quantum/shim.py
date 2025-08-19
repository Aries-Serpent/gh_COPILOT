
# Non-prod quantum shim (stubs)
from typing import Any


def run_phase_estimation(circuit: Any, **kwargs: Any) -> Any: ...


def run_vqe(ansatz: Any, hamiltonian: Any, **kwargs: Any) -> Any: ...


def run_anneal(problem: Any, adapter: str = "anneal") -> Any: ...
