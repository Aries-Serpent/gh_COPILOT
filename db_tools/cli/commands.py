"""
Command-line interface for database tools.
Provides backward-compatible access to all database operations.
"""

import argparse
import sys
from pathlib import Path

from utils.cross_platform_paths import CrossPlatformPathManager

from ..operations.access import DatabaseAccessLayer
from ..operations.cleanup import DatabaseCleanupProcessor
from ..operations.compliance import DatabaseComplianceChecker


class DatabaseCLI:
    """Unified CLI for database tools"""

    def __init__(self):
        self.commands = {
            'access': self.run_access_layer,
            'cleanup': self.run_cleanup_processor,
            'compliance': self.run_compliance_checker,
        }

    def create_parser(self) -> argparse.ArgumentParser:
        """Create command line parser"""
        parser = argparse.ArgumentParser(
            description="Database Tools CLI",
            prog="db_tools"
        )

        subparsers = parser.add_subparsers(
            dest='command',
            help='Available commands'
        )

        # Access layer command
        access_parser = subparsers.add_parser(
            'access',
            help='Database access layer operations'
        )
        access_parser.add_argument(
            '--operation',
            default='process',
            help='Operation to perform'
        )
        access_parser.add_argument(
            '--database',
            default=str(
                CrossPlatformPathManager.get_workspace_path()
                / 'databases'
                / 'production.db'
            ),
            help='Database path'
        )

        # Cleanup processor command
        cleanup_parser = subparsers.add_parser(
            'cleanup',
            help='Database cleanup operations'
        )
        cleanup_parser.add_argument(
            '--batch-size',
            type=int,
            default=1000,
            help='Batch size for processing'
        )
        cleanup_parser.add_argument(
            '--workspace',
            help='Workspace path'
        )

        # Compliance checker command
        compliance_parser = subparsers.add_parser(
            'compliance',
            help='Database compliance checking'
        )
        compliance_parser.add_argument(
            '--workspace',
            help='Workspace path'
        )

        return parser

    def run_access_layer(self, args) -> bool:
        """Run database access layer"""
        try:
            if not args.database:
                print("Error: --database path required")
                return False

            processor = DatabaseAccessLayer(args.database)
            return processor.execute_processing()
        except Exception as e:
            print(f"Error running access layer: {e}")
            return False

    def run_cleanup_processor(self, args) -> bool:
        """Run database cleanup processor"""
        try:
            workspace = args.workspace or str(Path.cwd())
            processor = DatabaseCleanupProcessor(workspace)
            results = processor.execute_cleanup(args.batch_size)

            print("\nCleanup Results:")
            print(f"  Total Checked: {results['total_checked']}")
            print(f"  Already Fixed: {results['already_fixed']}")
            print(f"  Still Pending: {results['still_pending']}")

            return True
        except Exception as e:
            print(f"Error running cleanup processor: {e}")
            return False

    def run_compliance_checker(self, args) -> bool:
        """Run database compliance checker"""
        try:
            workspace = args.workspace or str(Path.cwd())
            checker = DatabaseComplianceChecker(workspace)
            success = checker.execute_correction()

            # Display statistics
            stats = checker.get_correction_stats()
            print("\nCompliance Check Results:")
            print(f"  Total attempts: {stats['total']}")
            print(f"  Successful: {stats['successful']}")
            print(f"  Failed: {stats['failed']}")

            return success
        except Exception as e:
            print(f"Error running compliance checker: {e}")
            return False

    def run(self, args=None) -> int:
        """Run CLI with given arguments"""
        parser = self.create_parser()
        parsed_args = parser.parse_args(args)

        if not parsed_args.command:
            parser.print_help()
            return 1

        command_func = self.commands.get(parsed_args.command)
        if not command_func:
            print(f"Unknown command: {parsed_args.command}")
            return 1

        try:
            success = command_func(parsed_args)
            return 0 if success else 1
        except Exception as exc:
            print(f"Command execution failed: {exc}")
            return 1


def main():
    """Main CLI entry point"""
    cli = DatabaseCLI()
    return cli.run()


if __name__ == "__main__":
    sys.exit(main())
