"""Performance optimization utilities for quantum algorithms."""

import time
from typing import Dict, Any, Optional
import logging

try:  # pragma: no cover - psutil is optional
    import psutil  # type: ignore
except ImportError:  # pragma: no cover - fallback
    psutil = None  # type: ignore[assignment]


class PerformanceOptimizer:
    """Performance optimization utilities for quantum algorithms"""

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.performance_data = {}
    
    def monitor_execution(self, algorithm_name: str, execution_func, *args, **kwargs) -> Dict[str, Any]:
        """Monitor performance during algorithm execution"""
        if psutil is not None:
            # Get initial system state
            process = psutil.Process()
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            initial_cpu_percent = process.cpu_percent()
        else:  # pragma: no cover - executed when psutil missing
            process = None
            initial_memory = 0.0
            initial_cpu_percent = 0.0
        
        start_time = time.perf_counter()
        
        try:
            # Execute the algorithm
            result = execution_func(*args, **kwargs)
            success = True
            error = None
        except Exception as e:
            result = None
            success = False
            error = str(e)
        
        end_time = time.perf_counter()
        
        if process is not None:
            # Get final system state
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            final_cpu_percent = process.cpu_percent()
        else:  # pragma: no cover - executed when psutil missing
            final_memory = 0.0
            final_cpu_percent = 0.0
        
        performance_metrics = {
            'algorithm': algorithm_name,
            'execution_time': end_time - start_time,
            'success': success,
            'error': error,
            'result': result,
            'memory_usage': {
                'initial_mb': initial_memory,
                'final_mb': final_memory,
                'peak_mb': max(initial_memory, final_memory),
                'delta_mb': final_memory - initial_memory
            },
            'cpu_usage': {
                'initial_percent': initial_cpu_percent,
                'final_percent': final_cpu_percent
            },
            'timestamp': start_time
        }
        
        # Store performance data
        if algorithm_name not in self.performance_data:
            self.performance_data[algorithm_name] = []
        self.performance_data[algorithm_name].append(performance_metrics)
        
        return performance_metrics
    
    def get_performance_summary(self, algorithm_name: Optional[str] = None) -> Dict[str, Any]:
        """Get performance summary for algorithm(s)"""
        if algorithm_name:
            data = self.performance_data.get(algorithm_name, [])
            if not data:
                return {'algorithm': algorithm_name, 'executions': 0}
            
            execution_times = [d['execution_time'] for d in data]
            memory_deltas = [d['memory_usage']['delta_mb'] for d in data]
            success_count = sum(1 for d in data if d['success'])
            
            return {
                'algorithm': algorithm_name,
                'executions': len(data),
                'success_rate': success_count / len(data),
                'avg_execution_time': sum(execution_times) / len(execution_times),
                'min_execution_time': min(execution_times),
                'max_execution_time': max(execution_times),
                'avg_memory_delta': sum(memory_deltas) / len(memory_deltas),
                'max_memory_delta': max(memory_deltas),
                'min_memory_delta': min(memory_deltas)
            }
        else:
            # Summary for all algorithms
            summary = {}
            for alg_name in self.performance_data:
                summary[alg_name] = self.get_performance_summary(alg_name)
            return summary
    
    def optimize_batch_size(self, algorithm_name: str, base_batch_size: int = 100) -> int:
        """Recommend optimal batch size based on performance history"""
        data = self.performance_data.get(algorithm_name, [])
        if not data:
            return base_batch_size
        
        # Simple heuristic based on memory usage
        avg_memory_delta = sum(d['memory_usage']['delta_mb'] for d in data) / len(data)
        
        if avg_memory_delta > 100:  # High memory usage
            return max(base_batch_size // 2, 10)
        elif avg_memory_delta < 10:  # Low memory usage
            return min(base_batch_size * 2, 1000)
        else:
            return base_batch_size
    
    def clear_performance_data(self, algorithm_name: Optional[str] = None) -> None:
        """Clear performance data"""
        if algorithm_name:
            self.performance_data.pop(algorithm_name, None)
        else:
            self.performance_data.clear()
    
    def get_resource_recommendations(self) -> Dict[str, Any]:
        """Get resource usage recommendations"""
        if not self.performance_data:
            return {'recommendation': 'No performance data available'}
        
        all_data = []
        for algorithm_data in self.performance_data.values():
            all_data.extend(algorithm_data)
        
        if not all_data:
            return {'recommendation': 'No execution data available'}
        
        avg_memory = sum(d['memory_usage']['peak_mb'] for d in all_data) / len(all_data)
        max_memory = max(d['memory_usage']['peak_mb'] for d in all_data)
        avg_time = sum(d['execution_time'] for d in all_data) / len(all_data)
        
        recommendations = []
        
        if avg_memory > 500:
            recommendations.append("Consider reducing batch sizes or using memory-efficient algorithms")
        
        if avg_time > 30:
            recommendations.append("Consider parallel execution for long-running algorithms")
        
        if max_memory > 1000:
            recommendations.append("Monitor memory usage closely, consider adding memory limits")
        
        return {
            'avg_memory_mb': avg_memory,
            'max_memory_mb': max_memory,
            'avg_execution_time': avg_time,
            'recommendations': recommendations or ['Performance is within normal parameters']
        }