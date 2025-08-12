"""
Quantum algorithm execution manager with orchestration capabilities.
"""

import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional

try:  # pragma: no cover - optional dependency
    from qiskit import Aer
    QISKIT_AVAILABLE = True
except Exception:  # pragma: no cover - optional dependency
    Aer = None
    QISKIT_AVAILABLE = False

try:  # pragma: no cover - optional dependency
    from qiskit_ibm_provider import IBMProvider  # type: ignore  # noqa: F401
    HAS_IBM_PROVIDER = True
except Exception:  # pragma: no cover - optional dependency
    IBMProvider = None  # type: ignore  # noqa: F401
    HAS_IBM_PROVIDER = False

from ghc_quantum.ibm_backend import init_ibm_backend

from .registry import get_global_registry


class QuantumExecutor:
    """Manage execution of quantum algorithms with optional hardware backends."""
    
    def __init__(
        self,
        max_workers: int = 4,
        use_hardware: bool = False,
        backend_name: Optional[str] = None,
        token: str | None = None,
    ):
        self.max_workers = max_workers
        self.logger = logging.getLogger(__name__)
        self.registry = get_global_registry()
        self.execution_history: List[Dict[str, Any]] = []
        env_backend = os.getenv("IBM_BACKEND", "ibmq_qasm_simulator")
        self.backend_name = backend_name or env_backend
        self.backend = None
        self.token = token or os.getenv("QISKIT_IBM_TOKEN")
        env_use = os.getenv("QUANTUM_USE_HARDWARE", "0") == "1"
        self.use_hardware = use_hardware or bool(self.token) or env_use
        if self.use_hardware and not HAS_IBM_PROVIDER:
            self.logger.warning("IBM provider unavailable; attempting fallback")
        if self.use_hardware:
            backend, success = init_ibm_backend(
                token=self.token, backend_name=self.backend_name
            )
            self.backend = backend
            self.use_hardware = success
        elif QISKIT_AVAILABLE:
            self.backend = Aer.get_backend("qasm_simulator")

    def _load_backend(self, backend_name: str):
        """Load a Qiskit backend, falling back to simulation."""
        backend, success = init_ibm_backend(
            token=self.token, backend_name=backend_name
        )
        self.use_hardware = success
        if success:
            return backend
        if QISKIT_AVAILABLE:
            return Aer.get_backend("qasm_simulator")
        return None
    
    def execute_algorithm(self, algorithm_name: str, **kwargs) -> Dict[str, Any]:
        """Execute a single algorithm by name"""
        start_time = time.time()
        
        # Create algorithm instance
        algorithm = self.registry.create_algorithm(algorithm_name, **kwargs)
        if algorithm is None:
            result = {
                'algorithm': algorithm_name,
                'success': False,
                'error': f'Algorithm not found: {algorithm_name}',
                'execution_time': 0,
                'timestamp': start_time
            }
            self.execution_history.append(result)
            return result
        
        # Provide backend if algorithm supports it
        if hasattr(algorithm, "set_backend"):
            try:
                algorithm.set_backend(self.backend, use_hardware=self.use_hardware)
            except Exception as exc:  # pragma: no cover - optional method
                self.logger.warning("Failed to set backend: %s", exc)

        # Execute algorithm
        try:
            success = algorithm.execute_utility()
            execution_time = time.time() - start_time
            
            result = {
                'algorithm': algorithm_name,
                'success': success,
                'execution_time': execution_time,
                'timestamp': start_time,
                'stats': algorithm.get_execution_stats()
            }
            
            if not success:
                result['error'] = 'Algorithm execution failed'
            
        except Exception as e:
            execution_time = time.time() - start_time
            result = {
                'algorithm': algorithm_name,
                'success': False,
                'error': str(e),
                'execution_time': execution_time,
                'timestamp': start_time
            }
        
        self.execution_history.append(result)
        return result
    
    def execute_algorithms_parallel(self, algorithm_configs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute multiple algorithms in parallel"""
        results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all algorithms for execution
            future_to_config = {}
            for config in algorithm_configs:
                algorithm_name = config.pop('algorithm', None)
                if algorithm_name is None:
                    self.logger.error("Algorithm config missing 'algorithm' key")
                    continue
                
                future = executor.submit(self.execute_algorithm, algorithm_name, **config)
                future_to_config[future] = {'algorithm': algorithm_name, 'config': config}
            
            # Collect results as they complete
            for future in as_completed(future_to_config):
                config_info = future_to_config[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    error_result = {
                        'algorithm': config_info['algorithm'],
                        'success': False,
                        'error': f'Execution failed: {e}',
                        'execution_time': 0,
                        'timestamp': time.time()
                    }
                    results.append(error_result)
                    self.execution_history.append(error_result)
        
        return results
    
    def execute_algorithms_sequential(self, algorithm_configs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute multiple algorithms sequentially"""
        results = []
        
        for config in algorithm_configs:
            algorithm_name = config.pop('algorithm', None)
            if algorithm_name is None:
                self.logger.error("Algorithm config missing 'algorithm' key")
                continue
            
            result = self.execute_algorithm(algorithm_name, **config)
            results.append(result)
        
        return results
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """Get summary of all executions"""
        if not self.execution_history:
            return {
                'total_executions': 0,
                'successful_executions': 0,
                'failed_executions': 0,
                'success_rate': 0.0,
                'total_execution_time': 0.0,
                'algorithms_used': []
            }
        
        total_executions = len(self.execution_history)
        successful = sum(1 for r in self.execution_history if r.get('success', False))
        failed = total_executions - successful
        total_time = sum(r.get('execution_time', 0) for r in self.execution_history)
        algorithms_used = list(set(r.get('algorithm') for r in self.execution_history))
        
        return {
            'total_executions': total_executions,
            'successful_executions': successful,
            'failed_executions': failed,
            'success_rate': successful / total_executions if total_executions > 0 else 0.0,
            'total_execution_time': total_time,
            'algorithms_used': algorithms_used
        }
    
    def clear_history(self):
        """Clear execution history"""
        self.execution_history.clear()
    
    def get_algorithm_performance(self, algorithm_name: str) -> Dict[str, Any]:
        """Get performance metrics for a specific algorithm"""
        algorithm_executions = [r for r in self.execution_history if r.get('algorithm') == algorithm_name]
        
        if not algorithm_executions:
            return {
                'algorithm': algorithm_name,
                'executions': 0,
                'average_time': 0.0,
                'success_rate': 0.0,
                'fastest_time': 0.0,
                'slowest_time': 0.0
            }
        
        execution_times = [r.get('execution_time', 0) for r in algorithm_executions]
        successful = sum(1 for r in algorithm_executions if r.get('success', False))
        
        return {
            'algorithm': algorithm_name,
            'executions': len(algorithm_executions),
            'average_time': sum(execution_times) / len(execution_times),
            'success_rate': successful / len(algorithm_executions),
            'fastest_time': min(execution_times) if execution_times else 0.0,
            'slowest_time': max(execution_times) if execution_times else 0.0
        }