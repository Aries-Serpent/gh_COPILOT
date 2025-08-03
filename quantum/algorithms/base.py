"""
Base quantum algorithm class with standardized interface.
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


# Text-based indicators (NO Unicode emojis)  
TEXT_INDICATORS = {
    'start': '[START]',
    'success': '[SUCCESS]',
    'error': '[ERROR]',
    'info': '[INFO]',
    'progress': '[PROGRESS]',
}


class QuantumAlgorithmBase(ABC):
    """Base class for all quantum algorithms in the package"""
    
    def __init__(self, workspace_path: Optional[str] = None):
        self.workspace_path = Path(workspace_path or Path.cwd())
        self.logger = logging.getLogger(self.__class__.__name__)
        self.execution_stats = {}
    
    @abstractmethod
    def execute_algorithm(self) -> bool:
        """Execute the quantum algorithm - must be implemented by subclasses"""
        raise NotImplementedError
    
    @abstractmethod
    def get_algorithm_name(self) -> str:
        """Get the name of the algorithm"""
        raise NotImplementedError
    
    def execute_utility(self) -> bool:
        """Standardized utility execution with logging and timing"""
        start_time = datetime.now()
        algorithm_name = self.get_algorithm_name()
        
        self.logger.info(f"{TEXT_INDICATORS['start']} {algorithm_name} started: {start_time}")
        
        try:
            # Execute the algorithm
            success = self.execute_algorithm()
            
            # Calculate execution time
            duration = (datetime.now() - start_time).total_seconds()
            
            # Store execution statistics
            self.execution_stats = {
                'algorithm': algorithm_name,
                'start_time': start_time.isoformat(),
                'duration_seconds': duration,
                'success': success
            }
            
            if success:
                self.logger.info(
                    f"{TEXT_INDICATORS['success']} {algorithm_name} completed in {duration:.1f}s")
                return True
            else:
                self.logger.error(f"{TEXT_INDICATORS['error']} {algorithm_name} failed")
                return False
                
        except Exception as e:
            self.logger.error(f"{TEXT_INDICATORS['error']} {algorithm_name} error: {e}")
            return False
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics for the last run"""
        return self.execution_stats.copy()
    
    def validate_workspace(self) -> bool:
        """Validate workspace path exists and is accessible"""
        try:
            return self.workspace_path.exists() and self.workspace_path.is_dir()
        except Exception:
            return False
