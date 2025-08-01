"""
Quantum algorithm registry for managing and discovering algorithms.
"""

from typing import Dict, Type, List, Optional
import logging

from ..algorithms.base import QuantumAlgorithmBase
from ..algorithms.expansion import QuantumLibraryExpansion
from ..algorithms.functional import QuantumFunctional
from ..algorithms.clustering import QuantumClustering
from ..algorithms.teleportation import QuantumTeleportation


class QuantumAlgorithmRegistry:
    """Registry for quantum algorithms with plugin architecture"""
    
    def __init__(self):
        self.algorithms: Dict[str, Type[QuantumAlgorithmBase]] = {}
        self.logger = logging.getLogger(__name__)
        self._register_builtin_algorithms()
    
    def _register_builtin_algorithms(self):
        """Register built-in quantum algorithms"""
        self.register_algorithm("expansion", QuantumLibraryExpansion)
        self.register_algorithm("functional", QuantumFunctional)
        self.register_algorithm("clustering", QuantumClustering)
        self.register_algorithm("teleportation", QuantumTeleportation)
    
    def register_algorithm(self, name: str, algorithm_class: Type[QuantumAlgorithmBase]):
        """Register a quantum algorithm"""
        if not issubclass(algorithm_class, QuantumAlgorithmBase):
            raise ValueError(f"Algorithm {algorithm_class} must inherit from QuantumAlgorithmBase")
        
        self.algorithms[name] = algorithm_class
        self.logger.info(f"Registered quantum algorithm: {name}")
    
    def get_algorithm(self, name: str) -> Optional[Type[QuantumAlgorithmBase]]:
        """Get algorithm class by name"""
        return self.algorithms.get(name)
    
    def list_algorithms(self) -> List[str]:
        """List all registered algorithm names"""
        return list(self.algorithms.keys())
    
    def create_algorithm(self, name: str, **kwargs) -> Optional[QuantumAlgorithmBase]:
        """Create an instance of the specified algorithm"""
        algorithm_class = self.get_algorithm(name)
        if algorithm_class is None:
            self.logger.error(f"Algorithm not found: {name}")
            return None
        
        try:
            return algorithm_class(**kwargs)
        except Exception as e:
            self.logger.error(f"Failed to create algorithm {name}: {e}")
            return None
    
    def get_algorithm_info(self, name: str) -> Optional[Dict[str, str]]:
        """Get information about an algorithm"""
        algorithm_class = self.get_algorithm(name)
        if algorithm_class is None:
            return None
        
        # Create temporary instance to get algorithm name
        try:
            temp_instance = algorithm_class()
            return {
                'name': name,
                'class_name': algorithm_class.__name__,
                'algorithm_name': temp_instance.get_algorithm_name(),
                'module': algorithm_class.__module__,
            }
        except Exception as e:
            self.logger.warning(f"Could not get info for algorithm {name}: {e}")
            return {
                'name': name,
                'class_name': algorithm_class.__name__,
                'module': algorithm_class.__module__,
                'error': str(e)
            }


# Global registry instance
_global_registry = QuantumAlgorithmRegistry()


def get_global_registry() -> QuantumAlgorithmRegistry:
    """Get the global quantum algorithm registry"""
    return _global_registry


def register_algorithm(name: str, algorithm_class: Type[QuantumAlgorithmBase]):
    """Register an algorithm in the global registry"""
    _global_registry.register_algorithm(name, algorithm_class)


def get_algorithm(name: str) -> Optional[Type[QuantumAlgorithmBase]]:
    """Get algorithm from global registry"""
    return _global_registry.get_algorithm(name)


def list_algorithms() -> List[str]:
    """List algorithms in global registry"""
    return _global_registry.list_algorithms()