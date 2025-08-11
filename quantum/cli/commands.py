"""
Command-line interface for quantum tools.
Provides backward-compatible access to all quantum operations.
"""

import argparse
import sys
import json
from pathlib import Path

from ..orchestration.registry import get_global_registry
from ..orchestration.executor import QuantumExecutor
from ..quantum_compliance_engine import QuantumComplianceEngine


class QuantumCLI:
    """Unified CLI for quantum tools"""
    
    def __init__(self):
        self.registry = get_global_registry()
        self.executor = QuantumExecutor()
    
    def create_parser(self) -> argparse.ArgumentParser:
        """Create command line parser"""
        parser = argparse.ArgumentParser(
            description="Quantum Tools CLI",
            prog="quantum"
        )
        
        subparsers = parser.add_subparsers(
            dest='command',
            help='Available commands'
        )
        
        # List algorithms command
        list_parser = subparsers.add_parser(
            'list',
            help='List available quantum algorithms'
        )
        
        # Run algorithm command
        run_parser = subparsers.add_parser(
            'run',
            help='Run a quantum algorithm'
        )
        run_parser.add_argument(
            'algorithm',
            help='Algorithm to run'
        )
        run_parser.add_argument(
            '--workspace',
            help='Workspace path'
        )
        run_parser.add_argument(
            '--clusters',
            type=int,
            help='Number of clusters (for clustering algorithm)'
        )
        run_parser.add_argument(
            '--parallel',
            action='store_true',
            help='Run in parallel mode (if applicable)'
        )
        
        # Batch run command
        batch_parser = subparsers.add_parser(
            'batch',
            help='Run multiple algorithms'
        )
        batch_parser.add_argument(
            'config_file',
            help='JSON configuration file for batch execution'
        )
        batch_parser.add_argument(
            '--parallel',
            action='store_true',
            help='Run algorithms in parallel'
        )
        
        # Performance command
        perf_parser = subparsers.add_parser(
            'perf',
            help='Show performance statistics'
        )
        perf_parser.add_argument(
            '--algorithm',
            help='Show stats for specific algorithm'
        )
        perf_parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear performance history'
        )
        
        # Info command
        info_parser = subparsers.add_parser(
            'info',
            help='Show algorithm information'
        )
        info_parser.add_argument(
            'algorithm',
            help='Algorithm to show info for'
        )

        # Compliance command
        compliance_parser = subparsers.add_parser(
            'compliance',
            help='Run quantum compliance scoring on a file',
        )
        compliance_parser.add_argument('target', help='Target file to analyze')
        compliance_parser.add_argument(
            '--patterns', nargs='*', default=[], help='Patterns to match'
        )
        compliance_parser.add_argument(
            '--threshold', type=float, default=0.85, help='Score threshold'
        )
        
        return parser
    
    def list_algorithms(self, args) -> bool:
        """List available algorithms"""
        algorithms = self.registry.list_algorithms()
        
        if not algorithms:
            print("No algorithms registered")
            return True
        
        print("Available quantum algorithms:")
        for algorithm in algorithms:
            info = self.registry.get_algorithm_info(algorithm)
            if info:
                print(f"  {algorithm}: {info.get('algorithm_name', 'N/A')}")
                if 'error' in info:
                    print(f"    Error: {info['error']}")
            else:
                print(f"  {algorithm}: (info unavailable)")
        
        return True
    
    def run_algorithm(self, args) -> bool:
        """Run a single algorithm"""
        algorithm_name = args.algorithm
        
        if algorithm_name not in self.registry.list_algorithms():
            print(f"Algorithm '{algorithm_name}' not found")
            print("Available algorithms:", ", ".join(self.registry.list_algorithms()))
            return False
        
        # Prepare kwargs
        kwargs = {}
        if args.workspace:
            kwargs['workspace_path'] = args.workspace
        if hasattr(args, 'clusters') and args.clusters:
            kwargs['n_clusters'] = args.clusters
        
        print(f"Running {algorithm_name}...")
        result = self.executor.execute_algorithm(algorithm_name, **kwargs)
        
        if result['success']:
            print(f"✓ {algorithm_name} completed successfully")
            print(f"  Execution time: {result['execution_time']:.2f}s")
            
            if 'stats' in result and result['stats']:
                print("  Statistics:")
                stats = result['stats']
                for key, value in stats.items():
                    if key not in ['algorithm', 'start_time']:
                        print(f"    {key}: {value}")
        else:
            print(f"✗ {algorithm_name} failed")
            if 'error' in result:
                print(f"  Error: {result['error']}")
        
        return result['success']
    
    def run_batch(self, args) -> bool:
        """Run batch of algorithms"""
        try:
            with open(args.config_file, 'r') as f:
                configs = json.load(f)
        except Exception as e:
            print(f"Error reading config file: {e}")
            return False
        
        if not isinstance(configs, list):
            print("Config file must contain a list of algorithm configurations")
            return False
        
        print(f"Running {len(configs)} algorithms...")
        
        if args.parallel:
            results = self.executor.execute_algorithms_parallel(configs)
        else:
            results = self.executor.execute_algorithms_sequential(configs)
        
        # Summary
        successful = sum(1 for r in results if r.get('success', False))
        total = len(results)
        
        print(f"\nBatch execution completed: {successful}/{total} successful")
        
        for result in results:
            status = "✓" if result.get('success', False) else "✗"
            print(f"  {status} {result.get('algorithm', 'unknown')}: {result.get('execution_time', 0):.2f}s")
            if not result.get('success', False) and 'error' in result:
                print(f"      Error: {result['error']}")
        
        return successful == total
    
    def show_performance(self, args) -> bool:
        """Show performance statistics"""
        if args.clear:
            self.executor.clear_history()
            print("Performance history cleared")
            return True
        
        if args.algorithm:
            perf = self.executor.get_algorithm_performance(args.algorithm)
            if perf['executions'] == 0:
                print(f"No performance data for {args.algorithm}")
                return True
            
            print(f"Performance data for {args.algorithm}:")
            print(f"  Executions: {perf['executions']}")
            print(f"  Success rate: {perf['success_rate']:.1%}")
            print(f"  Average time: {perf['average_time']:.2f}s")
            print(f"  Fastest time: {perf['fastest_time']:.2f}s")
            print(f"  Slowest time: {perf['slowest_time']:.2f}s")
        else:
            summary = self.executor.get_execution_summary()
            if summary['total_executions'] == 0:
                print("No performance data available")
                return True
            
            print("Overall performance summary:")
            print(f"  Total executions: {summary['total_executions']}")
            print(f"  Success rate: {summary['success_rate']:.1%}")
            print(f"  Total execution time: {summary['total_execution_time']:.2f}s")
            print(f"  Algorithms used: {', '.join(summary['algorithms_used'])}")
        
        return True
    
    def show_algorithm_info(self, args) -> bool:
        """Show algorithm information"""
        info = self.registry.get_algorithm_info(args.algorithm)
        if not info:
            print(f"Algorithm '{args.algorithm}' not found")
            return False
        
        print(f"Algorithm: {args.algorithm}")
        print(f"  Name: {info.get('algorithm_name', 'N/A')}")
        print(f"  Class: {info.get('class_name', 'N/A')}")
        print(f"  Module: {info.get('module', 'N/A')}")
        
        if 'error' in info:
            print(f"  Error: {info['error']}")
        
        return True
    
    def run(self, args=None) -> int:
        """Run CLI with given arguments"""
        parser = self.create_parser()
        parsed_args = parser.parse_args(args)
        
        if not parsed_args.command:
            parser.print_help()
            return 1
        
        command_map = {
            'list': self.list_algorithms,
            'run': self.run_algorithm,
            'batch': self.run_batch,
            'perf': self.show_performance,
            'info': self.show_algorithm_info,
            'compliance': self.run_compliance,
        }
        
        command_func = command_map.get(parsed_args.command)
        if not command_func:
            print(f"Unknown command: {parsed_args.command}")
            return 1
        
        success = command_func(parsed_args)
        return 0 if success else 1

    def run_compliance(self, args) -> bool:
        """Run quantum compliance scoring on a file."""
        engine = QuantumComplianceEngine()
        score = engine.score(Path(args.target), args.patterns, threshold=args.threshold)
        print(f"Compliance score: {score:.4f}")
        return score >= args.threshold


def main():
    """Main CLI entry point"""
    cli = QuantumCLI()
    return cli.run()


if __name__ == "__main__":
    sys.exit(main())