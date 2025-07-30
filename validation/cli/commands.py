"""
Command-line interface for validation tools.
Provides unified access to all validation operations.
"""

import argparse
import json
import sys
from datetime import datetime
from typing import List
from pathlib import Path

from ..protocols.session import SessionProtocolValidator
from ..protocols.deployment import DeploymentValidator
from ..core.validators import (
    ValidationResult,
    ValidationStatus,
)
from ..reporting.formatters import ValidationReportFormatter


class ValidationCLI:
    """Unified CLI for validation tools"""

    def __init__(self):
        self.formatter = ValidationReportFormatter()

    def create_parser(self) -> argparse.ArgumentParser:
        """Create command line parser"""
        parser = argparse.ArgumentParser(
            description="Validation Tools CLI",
            prog="validation"
        )

        subparsers = parser.add_subparsers(
            dest='command',
            help='Available commands'
        )

        # Session validation command
        session_parser = subparsers.add_parser(
            'session',
            help='Run session protocol validation'
        )
        session_parser.add_argument(
            '--workspace',
            help='Workspace path'
        )
        session_parser.add_argument(
            '--comprehensive',
            action='store_true',
            help='Run comprehensive session validation'
        )

        # Deployment validation command
        deploy_parser = subparsers.add_parser(
            'deployment',
            help='Run deployment validation'
        )
        deploy_parser.add_argument(
            '--workspace',
            help='Workspace path'
        )

        # Comprehensive validation command
        comprehensive_parser = subparsers.add_parser(
            'comprehensive',
            help='Run all validations'
        )
        comprehensive_parser.add_argument(
            '--workspace',
            help='Workspace path'
        )
        comprehensive_parser.add_argument(
            '--output',
            help='Output file path for report'
        )
        comprehensive_parser.add_argument(
            '--format',
            choices=['json', 'markdown', 'text'],
            default='json',
            help='Report format'
        )

        # Report generation command
        report_parser = subparsers.add_parser(
            'report',
            help='Generate validation report'
        )
        report_parser.add_argument(
            'input_file',
            help='Input validation results file (JSON)'
        )
        report_parser.add_argument(
            '--output',
            help='Output file path'
        )
        report_parser.add_argument(
            '--format',
            choices=['json', 'markdown', 'text'],
            default='markdown',
            help='Report format'
        )

        return parser

    def run_session_validation(self, args) -> bool:
        """Run session validation"""
        try:
            validator = SessionProtocolValidator(args.workspace)

            if args.comprehensive:
                print("Running comprehensive session validation...")
                result = validator.validate_comprehensive_session()
            else:
                print("Running session protocol validation...")
                result = validator.validate_startup()

            self._print_result(result)
            return result.is_success

        except Exception as e:
            print(f"Error running session validation: {e}")
            return False

    def run_deployment_validation(self, args) -> bool:
        """Run deployment validation"""
        try:
            validator = DeploymentValidator(args.workspace)
            print("Running deployment validation...")
            result = validator.validate_final_deployment_status()

            self._print_result(result)
            return result.is_success

        except Exception as e:
            print(f"Error running deployment validation: {e}")
            return False

    def run_comprehensive_validation(self, args) -> bool:
        """Run comprehensive validation"""
        try:
            print("Running comprehensive validation...")

            # Run all validators
            session_validator = SessionProtocolValidator(args.workspace)
            deployment_validator = DeploymentValidator(args.workspace)

            session_result = session_validator.validate_comprehensive_session()
            deployment_result = deployment_validator.validate_final_deployment_status()

            results = [session_result, deployment_result]

            # Print individual results
            print("\n" + "="*60)
            print("COMPREHENSIVE VALIDATION RESULTS")
            print("="*60)

            for i, result in enumerate(results, 1):
                print(f"\n{i}. {result.message}")
                if result.errors:
                    for error in result.errors:
                        print(f"   Error: {error}")
                if result.warnings:
                    for warning in result.warnings:
                        print(f"   Warning: {warning}")

            # Generate report if requested
            if args.output:
                output_path = Path(args.output)
                success = self.formatter.save_report(
                    results, output_path, args.format, "Comprehensive Validation Report"
                )
                if success:
                    print(f"\nReport saved to: {output_path}")
                else:
                    print("\nFailed to save report")

            # Determine overall success
            overall_success = all(result.is_success for result in results)

            # Print summary
            passed = sum(1 for r in results if r.is_success)
            total = len(results)

            print("\n" + "=" * 60)
            print(f"SUMMARY: {passed}/{total} validations passed")
            if overall_success:
                print("✓ COMPREHENSIVE VALIDATION PASSED")
            else:
                print("✗ COMPREHENSIVE VALIDATION FAILED")
            print("="*60)

            return overall_success

        except Exception as e:
            print(f"Error running comprehensive validation: {e}")
            return False

    def generate_report(self, args) -> bool:
        """Generate validation report from existing results"""
        try:
            with open(args.input_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            results: List[ValidationResult] = []
            for item in data.get("results", []):
                try:
                    status_enum = ValidationStatus(item.get("status", "passed"))
                except ValueError:
                    status_enum = ValidationStatus.PASSED
                timestamp = item.get("timestamp")
                ts = datetime.fromisoformat(timestamp) if timestamp else datetime.now()
                results.append(
                    ValidationResult(
                        status=status_enum,
                        message=item.get("message", ""),
                        details=item.get("details", {}),
                        errors=item.get("errors", []),
                        warnings=item.get("warnings", []),
                        timestamp=ts,
                    )
                )

            output_path = Path(args.output) if args.output else Path(args.input_file)
            saved = self.formatter.save_report(
                results,
                output_path,
                args.format,
                data.get("title", "Validation Report"),
            )
            if saved:
                print(f"Report saved to: {output_path.with_suffix('.' + args.format)}")
            else:
                print("Failed to save report")
            return saved

        except Exception as e:
            print(f"Error generating report: {e}")
            return False

    def _print_result(self, result: ValidationResult):
        """Print validation result"""
        status_symbol = self._get_status_symbol(result)
        print(f"\n{status_symbol} {result.message}")

        if result.errors:
            print("Errors:")
            for error in result.errors:
                print(f"  - {error}")

        if result.warnings:
            print("Warnings:")
            for warning in result.warnings:
                print(f"  - {warning}")

        if result.details:
            print("Details:")
            for key, value in result.details.items():
                print(f"  {key}: {value}")

    def _get_status_symbol(self, result: ValidationResult) -> str:
        """Get status symbol for result"""
        from ..core.validators import ValidationStatus

        symbols = {
            ValidationStatus.PASSED: "✓",
            ValidationStatus.FAILED: "✗",
            ValidationStatus.WARNING: "⚠",
            ValidationStatus.ERROR: "💥",
            ValidationStatus.SKIPPED: "⏭"
        }
        return symbols.get(result.status, "?")

    def run(self, args=None) -> int:
        """Run CLI with given arguments"""
        parser = self.create_parser()
        parsed_args = parser.parse_args(args)

        if not parsed_args.command:
            parser.print_help()
            return 1

        command_map = {
            'session': self.run_session_validation,
            'deployment': self.run_deployment_validation,
            'comprehensive': self.run_comprehensive_validation,
            'report': self.generate_report
        }

        command_func = command_map.get(parsed_args.command)
        if not command_func:
            print(f"Unknown command: {parsed_args.command}")
            return 1

        success = command_func(parsed_args)
        return 0 if success else 1


def main():
    """Main CLI entry point"""
    cli = ValidationCLI()
    return cli.run()


if __name__ == "__main__":
    sys.exit(main())
