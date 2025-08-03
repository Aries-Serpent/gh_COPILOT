# QUANTUM OPTIMIZER MODULE: ENTERPRISE-GRADE QUANTUM-INSPIRED OPTIMIZATION ENGINE
# > Generated: 2025-07-24 19:36:07 | Author: mbaetiong

from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple

from utils.cross_platform_paths import CrossPlatformPathManager
from pathlib import Path
import os
import warnings

import numpy as np

try:  # pragma: no cover - import check
    from qiskit import Aer
    from qiskit.primitives import Estimator
    from qiskit.quantum_info import SparsePauliOp
    from qiskit.circuit.library import TwoLocal
    try:
        from qiskit.algorithms.minimum_eigensolvers import QAOA, VQE
        from qiskit.algorithms.optimizers import COBYLA
    except Exception:
        from qiskit_algorithms.minimum_eigensolvers import QAOA, VQE  # type: ignore
        from qiskit_algorithms.optimizers import COBYLA  # type: ignore
    QISKIT_AVAILABLE = True
except Exception:  # pragma: no cover - qiskit optional
    QISKIT_AVAILABLE = False
    Aer = Estimator = SparsePauliOp = TwoLocal = QAOA = VQE = COBYLA = None  # type: ignore

from quantum.ibm_backend import init_ibm_backend

# Expose IBMProvider for monkeypatching in tests
try:  # pragma: no cover - optional dependency
    from qiskit_ibm_provider import IBMProvider
except Exception:  # pragma: no cover - provider may be missing
    IBMProvider = None

# --- Anti-Recursion Validation ---

def chunk_anti_recursion_validation() -> bool:
    """Run all anti-recursion checks.

    Returns ``True`` when the workspace and backup paths are safe.
    Raises ``RuntimeError`` with details on failure.
    """

    validate_no_recursive_folders()
    offending = detect_c_temp_violations()
    if offending:
        raise RuntimeError(f"CRITICAL: E:/temp/ violations prevent chunk execution: {offending}")
    return True


def validate_workspace() -> bool:
    """Public entry point to trigger anti-recursion validation."""

    return chunk_anti_recursion_validation()


def validate_no_recursive_folders() -> None:
    """Ensure workspace and backup directories are distinct and non-nesting.

    Walks both roots resolving symlinks and comparing inodes so that no
    subdirectory can link back to either root.
    """

    workspace = CrossPlatformPathManager.get_workspace_path().resolve()
    backup_root = CrossPlatformPathManager.get_backup_root().resolve()

    if workspace == backup_root:
        raise RuntimeError(f"Workspace and backup root are identical: {workspace}")
    if workspace in backup_root.parents:
        raise RuntimeError(
            f"Backup root {backup_root} cannot reside within workspace {workspace}"
        )
    if backup_root in workspace.parents:
        raise RuntimeError(
            f"Workspace {workspace} cannot reside within backup root {backup_root}"
        )

    workspace_inode = workspace.stat().st_ino
    backup_inode = backup_root.stat().st_ino

    def is_nested(child: Path, parent: Path) -> bool:
        try:
            child.relative_to(parent)
            return True
        except ValueError:
            return False

    for base, target in ((workspace, backup_root), (backup_root, workspace)):
        for root, dirs, _ in os.walk(base, followlinks=True):
            for d in dirs:
                path = Path(root) / d
                try:
                    resolved = path.resolve()
                    inode = resolved.stat().st_ino
                except OSError:
                    continue
                if inode in {workspace_inode, backup_inode} or resolved in {
                    workspace,
                    backup_root,
                }:
                    raise RuntimeError(f"Subdirectory {path} links back to {resolved}")
                if is_nested(resolved, target):
                    raise RuntimeError(
                        f"Subdirectory {path} nests within {target}: {resolved}"
                    )


def detect_c_temp_violations() -> Optional[str]:
    forbidden = ["E:/temp/", "E:\\temp\\"]
    workspace = str(CrossPlatformPathManager.get_workspace_path())
    backup_root = str(CrossPlatformPathManager.get_backup_root())
    for forbidden_path in forbidden:
        if workspace.startswith(forbidden_path):
            return workspace
        if backup_root.startswith(forbidden_path):
            return backup_root
    return None

# --- Quantum Optimizer Class ---

class QuantumOptimizer:
    """
    Enterprise-grade quantum-inspired optimizer supporting classical and hybrid (quantum-classical) routines.

    Features:
    - Supports classical optimizers (simulated annealing, basin-hopping)
    - Provides QAOA and VQE stubs if Qiskit is available
    - Unified run interface with progress reporting
    - Logs optimization metrics for compliance and reproducibility
    """

    def __init__(
        self,
        objective_function: Callable,
        variable_bounds: List[Tuple[float, float]],
        method: str = "simulated_annealing",
        options: Optional[Dict[str, Any]] = None,
        backend: Any = None,
        use_hardware: bool = False,
        validate_workspace: bool = False,
    ):
        """Initialize optimizer."""
        self.objective_function = objective_function
        self.variable_bounds = variable_bounds
        self.method = method
        self.options = options or {}
        self.history: List[Dict[str, Any]] = []
        self.metrics: Dict[str, Any] = {}
        self.backend = backend
        self.use_hardware = use_hardware
        if validate_workspace:
            chunk_anti_recursion_validation()
        self._validate_init()

    def set_backend(
        self,
        backend: Any | None,
        use_hardware: bool = False,
        token_env: str = "QISKIT_IBM_TOKEN",
    ) -> None:
        """Set quantum backend for optimizers.

        When ``use_hardware`` is True and ``backend`` is ``None``, this method
        attempts to initialize an IBM backend via :func:`init_ibm_backend`.
        ``use_hardware`` is updated based on the availability of the hardware
        backend. The chosen backend is logged with a ``[QUANTUM_BACKEND]`` tag.
        """
        if use_hardware and backend is None:
            if IBMProvider is None:
                warnings.warn(
                    "IBMProvider not available; using simulator",
                )
                backend = (
                    Aer.get_backend("aer_simulator") if QISKIT_AVAILABLE else None
                )
                self.backend = backend
                self.use_hardware = False
            else:
                backend, success = init_ibm_backend(token_env=token_env)
                if not success:
                    warnings.warn(
                        "Hardware backend initialization failed; using simulator",
                    )
                self.backend = backend
                self.use_hardware = success
        else:
            self.backend = backend
            self.use_hardware = use_hardware
        backend_name = getattr(self.backend, "name", str(self.backend))
        self.log_event("[QUANTUM_BACKEND]", {"backend": backend_name, "hardware": self.use_hardware})

    def configure_backend(
        self,
        backend_name: str = "ibmq_qasm_simulator",
        use_hardware: bool = False,
        token: Optional[str] = None,
    ) -> Any:
        """Acquire and configure an IBM quantum backend.

        Attempts to load credentials from ``QISKIT_IBM_TOKEN`` if ``token`` is
        not provided. If hardware access fails or the provider is unavailable,
        the optimizer falls back to the local ``Aer`` simulator.
        """
        if use_hardware:
            if token:
                os.environ.setdefault("QISKIT_IBM_TOKEN", token)
            os.environ.setdefault("IBM_BACKEND", backend_name)
            backend, success = init_ibm_backend()
            self.set_backend(backend, success)
            if success:
                return backend
        if QISKIT_AVAILABLE:
            simulator = Aer.get_backend("statevector_simulator")
            self.set_backend(simulator, False)
            return simulator
        raise ImportError("No quantum backend available")

    def _validate_init(self):
        if not callable(self.objective_function):
            raise ValueError("objective_function must be callable")
        if (
            not isinstance(self.variable_bounds, list)
            or not all(
                isinstance(t, tuple) and len(t) == 2 for t in self.variable_bounds
            )
        ):
            raise ValueError(
                "variable_bounds must be a list of (min, max) tuples"
            )
        if self.method.lower() not in {"simulated_annealing", "basin_hopping", "qaoa", "vqe"}:
            raise ValueError(f"Unsupported optimizer method: {self.method}")

    def log_event(self, event: str, data: Optional[Dict[str, Any]] = None):
        # Log structure: append to self.history and optionally print event
        entry = {"timestamp": datetime.utcnow().isoformat() + "Z", "event": event}
        if data:
            entry.update(data)
        self.history.append(entry)
        # Optionally, persist to analytics.db or compliance logs

    def run(self, x0: Optional[np.ndarray] = None, **kwargs) -> Dict[str, Any]:
        """
        Run the selected optimization routine.

        Args:
            x0: Initial guess for variables (if required by method).
            backend_name: Optional IBM backend name when requesting hardware.
            token: Optional IBM Quantum API token.
            kwargs: Additional arguments passed to optimizer.

        Returns:
            Dictionary containing result, metrics, and full history.
        """
        backend_name = kwargs.pop("backend_name", "ibmq_qasm_simulator")
        token = kwargs.pop("token", None)
        if self.use_hardware and self.backend is None:
            try:
                self.configure_backend(
                    backend_name=backend_name, use_hardware=True, token=token
                )
            except Exception:
                self.use_hardware = False

        self.log_event("optimization_start", {"method": self.method, "bounds": self.variable_bounds})
        start_time = datetime.utcnow()
        result = None

        if self.method == "simulated_annealing":
            result = self._run_simulated_annealing(x0, **kwargs)
        elif self.method == "basin_hopping":
            result = self._run_basin_hopping(x0, **kwargs)
        elif self.method == "qaoa":
            if QISKIT_AVAILABLE:
                result = self._run_qaoa(**kwargs)
            else:
                raise ImportError("Qiskit is required for QAOA optimizer")
        elif self.method == "vqe":
            if QISKIT_AVAILABLE:
                result = self._run_vqe(**kwargs)
            else:
                raise ImportError("Qiskit is required for VQE optimizer")
        else:
            raise ValueError(f"Unknown optimizer method: {self.method}")

        elapsed = (datetime.utcnow() - start_time).total_seconds()
        self.metrics["elapsed_seconds"] = elapsed
        self.log_event(
            "optimization_complete",
            {
                "elapsed_seconds": elapsed,
                "best_result": result.get("best_result") if result else None,
            },
        )
        summary = {
            "result": result,
            "metrics": self.metrics,
            "history": self.history
        }
        return summary

    def _run_simulated_annealing(
        self,
        x0: Optional[np.ndarray],
        max_iter: int = 500,
        temp: float = 1.0,
        cooling: float = 0.95,
    ) -> Dict[str, Any]:
        """Simple simulated annealing optimizer (classical, for demonstration)."""
        dim = len(self.variable_bounds)
        if x0 is None:
            x0 = np.array([(a + b) / 2 for a, b in self.variable_bounds])
        x = np.array(x0)
        best_x = x.copy()
        best_val = self.objective_function(x)
        current_temp = temp
        for i in range(max_iter):
            x_new = x + np.random.uniform(-0.1, 0.1, size=dim)
            for j, (a, b) in enumerate(self.variable_bounds):
                x_new[j] = np.clip(x_new[j], a, b)
            val_new = self.objective_function(x_new)
            if val_new < best_val or np.exp((best_val - val_new) / (current_temp + 1e-8)) > np.random.rand():
                x = x_new
                best_val = val_new
                best_x = x.copy()
            current_temp *= cooling
            if i % max(1, max_iter // 10) == 0:
                self.log_event(
                    "annealing_progress",
                    {
                        "iteration": i,
                        "temperature": current_temp,
                        "current_best": best_val,
                    },
                )
        return {"best_result": best_x.tolist(), "best_value": float(best_val)}

    def _run_basin_hopping(self, x0: Optional[np.ndarray], niter: int = 100) -> Dict[str, Any]:
        """Basin-hopping optimizer using scipy (if available), else fallback to random restarts."""
        try:
            from scipy.optimize import basinhopping
            if x0 is None:
                x0 = np.array([(a + b) / 2 for a, b in self.variable_bounds])
            minimizer_kwargs = {
                "method": "L-BFGS-B",
                "bounds": self.variable_bounds
            }
            result = basinhopping(self.objective_function, x0, niter=niter, minimizer_kwargs=minimizer_kwargs)
            self.log_event("basin_hopping_complete", {"fun": float(result.fun), "x": result.x.tolist()})
            return {"best_result": result.x.tolist(), "best_value": float(result.fun)}
        except ImportError:
            # Fallback: random restarts
            best_x = None
            best_val = float("inf")
            for i in range(niter):
                x = np.array([np.random.uniform(a, b) for a, b in self.variable_bounds])
                val = self.objective_function(x)
                if val < best_val:
                    best_val = val
                    best_x = x.copy()
                if i % max(1, niter // 10) == 0:
                    self.log_event("basin_hopping_progress", {"iteration": i, "current_best": best_val})
            return {"best_result": best_x.tolist(), "best_value": float(best_val)}

    def _get_estimator(self) -> Any:
        """Create an estimator for the current backend with hardware fallback."""
        if not QISKIT_AVAILABLE:
            raise ImportError("Qiskit is required for quantum estimators")
        if self.backend is not None:
            try:
                return Estimator(backend=self.backend)
            except Exception:
                backend_name = getattr(self.backend, "name", str(self.backend))
                self.log_event("backend_fallback", {"backend": backend_name})
                self.backend = Aer.get_backend("statevector_simulator")
                self.use_hardware = False
                return Estimator(backend=self.backend)
        return Estimator()

    def _run_qaoa(self, **kwargs) -> Dict[str, Any]:
        """Run QAOA using Qiskit's minimum eigensolver API."""
        n_qubits = kwargs.get("n_qubits", len(self.variable_bounds) or 2)
        reps = kwargs.get("reps", 1)
        max_iter = kwargs.get("max_iter", 100)
        estimator = self._get_estimator()
        optimizer = COBYLA(maxiter=max_iter)
        ansatz = TwoLocal(n_qubits, "ry", "cz", reps=reps)
        interval = max(1, max_iter // 10)

        def callback(eval_count, params, mean, _):
            if eval_count % interval == 0:
                self.log_event("qaoa_progress", {"eval_count": eval_count, "mean": float(mean)})

        qaoa = QAOA(ansatz=ansatz, optimizer=optimizer, estimator=estimator, callback=callback)
        hamiltonian = SparsePauliOp.from_list([("Z" * n_qubits, 1.0)])
        self.log_event("qaoa_start", {"n_qubits": n_qubits, "reps": reps})
        result = qaoa.compute_minimum_eigenvalue(hamiltonian)
        energy = float(result.eigenvalue.real)
        self.log_event("qaoa_complete", {"energy": energy})
        return {"eigenvalue": energy}

    def _run_vqe(self, **kwargs) -> Dict[str, Any]:
        """Run VQE using Qiskit's minimum eigensolver API."""
        n_qubits = kwargs.get("n_qubits", len(self.variable_bounds) or 2)
        reps = kwargs.get("reps", 1)
        max_iter = kwargs.get("max_iter", 100)
        estimator = self._get_estimator()
        optimizer = COBYLA(maxiter=max_iter)
        ansatz = TwoLocal(n_qubits, "ry", "cz", reps=reps)
        interval = max(1, max_iter // 10)

        def callback(eval_count, params, mean, _):
            if eval_count % interval == 0:
                self.log_event("vqe_progress", {"eval_count": eval_count, "mean": float(mean)})

        vqe = VQE(ansatz=ansatz, optimizer=optimizer, estimator=estimator, callback=callback)
        hamiltonian = SparsePauliOp.from_list([("Z" * n_qubits, 1.0)])
        self.log_event("vqe_start", {"n_qubits": n_qubits, "reps": reps})
        result = vqe.compute_minimum_eigenvalue(hamiltonian)
        energy = float(result.eigenvalue.real)
        self.log_event("vqe_complete", {"energy": energy})
        return {"eigenvalue": energy}

# --- Example Usage ---

if __name__ == "__main__":
    # Example: Minimize a simple quadratic function
    def quad_obj(x):
        return np.sum((x - 2.0) ** 2)

    bounds = [(-5, 5), (-5, 5)]
    optimizer = QuantumOptimizer(objective_function=quad_obj, variable_bounds=bounds, method="simulated_annealing")
    summary = optimizer.run()
    print("Optimization result:")
    print(summary["result"])
    print("History:")
    for event in summary["history"]:
        print(event)
