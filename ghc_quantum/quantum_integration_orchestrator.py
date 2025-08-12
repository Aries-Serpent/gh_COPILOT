"""High-level orchestration for quantum algorithm execution.

Provides a simple interface that coordinates the algorithm registry and
executor. When quantum hardware is unavailable, the underlying executor
falls back to the local `qasm_simulator` so callers can rely on a
consistent API.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from ghc_quantum.orchestration.executor import QuantumExecutor
from ghc_quantum.orchestration.registry import get_global_registry


class QuantumIntegrationOrchestrator:
    """Coordinate execution of registered quantum algorithms."""

    def __init__(
        self,
        *,
        use_hardware: bool = False,
        backend_name: Optional[str] = None,
        max_workers: int = 4,
    ) -> None:
        self.executor = QuantumExecutor(
            max_workers=max_workers,
            use_hardware=use_hardware,
            backend_name=backend_name,
        )
        self.registry = get_global_registry()

    def run_algorithm(self, name: str, **kwargs: Any) -> Dict[str, Any]:
        """Execute a single algorithm by name."""
        return self.executor.execute_algorithm(name, **kwargs)

    def run_plan(self, algorithm_configs: List[Dict[str, Any]], *, parallel: bool = False) -> List[Dict[str, Any]]:
        """Execute multiple algorithms sequentially or in parallel."""
        if parallel:
            return self.executor.execute_algorithms_parallel(algorithm_configs)
        return self.executor.execute_algorithms_sequential(algorithm_configs)

    def available_algorithms(self) -> List[str]:
        """List algorithms registered with the global registry."""
        return self.registry.list_algorithms()

    def execution_summary(self) -> Dict[str, Any]:
        """Return aggregated statistics from the executor."""
        return self.executor.get_execution_summary()


__all__ = ["QuantumIntegrationOrchestrator"]
