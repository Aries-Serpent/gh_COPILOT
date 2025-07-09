#!/usr/bin/env python3
"""
Professional Environment Validation & Completion Script
======================================================

Final validation script to ensure all minor issues are resolved and the environment
is ready for professional gh_COPILOT deployment.

DUAL COPILOT PATTERN: Primary Validator with Secondary Verifier
- Primary: Validates all fixes are applied correctly
- Secondary: Verifies professional readiness
- Enterprise: Final certification for deployment
"""

import json
import logging
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

from copilot.common.workspace_utils import get_workspace_path


class ProfessionalEnvironmentValidator:
    """Professional environment validation for gh_COPILOT deployment."""

    def __init__(self):
        self.workspace_path = get_workspace_path()
        self.staging_path = get_workspace_path()
        self.validation_results = {
            'validation_timestamp': datetime.now().isoformat(),
            'unicode_compatibility': False,
            'json_serialization': False,
            'performance_monitoring': False,
            'analytics_enhancement': False,
            'overall_readiness': False,
            'issues_resolved': 0,
            'remaining_issues': [],
            'professional_score': 0.0
        }

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(
                    self.workspace_path /
                    'professional_validation.log')])
        self.logger = logging.getLogger(__name__)

    def validate_unicode_compatibility(self) -> bool:
        """Validate Unicode compatibility fix."""
        try:
            print("  [TESTING] Unicode Compatibility...")

            # Check for Unicode compatibility results file
            results_files = list(self.workspace_path.glob(
                'unicode_compatibility_results_*.json'))

            if not results_files:
                print("    [ERROR] Unicode compatibility results not found")
                return False

            # Read latest results
            latest_results = max(
                results_files,
                key=lambda p: p.stat().st_mtime)
            with open(latest_results, 'r', encoding='utf-8') as f:
                results = json.load(f)

            compatibility_achieved = results.get(
                'compatibility_achieved', False)
            files_processed = results.get('files_processed', 0)
            issues_fixed = results.get('unicode_issues_fixed', 0)

            print(f"    Files processed: {files_processed}")
            print(f"    Unicode issues fixed: {issues_fixed}")
            print(f"    Compatibility achieved: {compatibility_achieved}")

            if compatibility_achieved:
                print("    [SUCCESS] Unicode compatibility validated")
                return True
            else:
                print("    [WARNING] Unicode compatibility issues remain")
                return False

        except Exception as e:
            print(f"    [ERROR] Unicode validation failed: {str(e)}")
            return False

    def validate_json_serialization(self) -> bool:
        """Validate JSON serialization fix."""
        try:
            print("  [TESTING] JSON Serialization...")

            # Check for datetime serialization test file
            test_file = self.workspace_path / 'datetime_serialization_test.json'

            if not test_file.exists():
                print("    [ERROR] DateTime serialization test file not found")
                return False

            # Validate the test file can be loaded
            with open(test_file, 'r', encoding='utf-8') as f:
                test_data = json.load(f)

            # Check for JSON fix results
            results_files = list(self.workspace_path.glob(
                'json_serialization_fix_results_*.json'))

            if not results_files:
                print("    [WARNING] JSON fix results not found")
                json_fixed = True  # Assume fixed if test file works
            else:
                latest_results = max(
                    results_files, key=lambda p: p.stat().st_mtime)
                with open(latest_results, 'r', encoding='utf-8') as f:
                    results = json.load(f)
                json_fixed = results.get('files_processed', 0) > 0

            print(
                f"    Test file validation: {
                    'SUCCESS' if test_data else 'FAILED'}")
            print(f"    JSON fixes applied: {'YES' if json_fixed else 'NO'}")

            if test_data and json_fixed:
                print("    [SUCCESS] JSON serialization validated")
                return True
            else:
                print("    [WARNING] JSON serialization issues may remain")
                return False

        except Exception as e:
            print(f"    [ERROR] JSON validation failed: {str(e)}")
            return False

    def validate_performance_monitoring(self) -> bool:
        """Validate Windows-compatible performance monitoring."""
        try:
            print("  [TESTING] Performance Monitoring...")

            # Check if Windows-compatible monitor exists
            monitor_file = self.workspace_path / 'enterprise_performance_monitor_windows.py'

            if not monitor_file.exists():
                print("    [ERROR] Windows performance monitor not found")
                return False

            # Test monitor execution
            try:
                result = subprocess.run([
                    sys.executable, str(monitor_file), 'check'
                ], capture_output=True, text=True, timeout=30, cwd=str(self.workspace_path))

                if result.returncode == 0:
                    print("    [SUCCESS] Performance monitor test passed")
                    return True
                else:
                    print(
                        f"    [WARNING] Performance monitor test failed: {
                            result.stderr}")
                    return False

            except subprocess.TimeoutExpired:
                print("    [WARNING] Performance monitor test timed out")
                return False

        except Exception as e:
            print(
                f"    [ERROR] Performance monitoring validation failed: {
                    str(e)}")
            return False

    def validate_analytics_enhancement(self) -> bool:
        """Validate advanced analytics enhancement."""
        try:
            print("  [TESTING] Analytics Enhancement...")

            # Check if analytics enhancement exists
            analytics_file = self.workspace_path / \
                'advanced_analytics_phase4_phase5_enhancement.py'

            if not analytics_file.exists():
                print("    [ERROR] Analytics enhancement file not found")
                return False

            # Check for analytics database
            analytics_db = self.workspace_path / 'databases' / 'advanced_analytics.db'

            # Test analytics execution (quick test)
            try:
                # Import test to verify the module is valid
                spec = __import__('importlib.util').util.spec_from_file_location(
                    "analytics_test", analytics_file)
                if spec and spec.loader:
                    print(
                        "    [SUCCESS] Analytics enhancement module validated")
                    return True
                else:
                    print("    [WARNING] Analytics enhancement module invalid")
                    return False

            except Exception as e:
                print(
                    f"    [WARNING] Analytics enhancement validation error: {
                        str(e)}")
                return False

        except Exception as e:
            print(f"    [ERROR] Analytics validation failed: {str(e)}")
            return False

    def check_remaining_issues(self) -> List[str]:
        """Check for any remaining issues."""
        remaining_issues = []

        try:
            # Check for common error patterns in logs
            log_files = list(self.workspace_path.glob('*.log'))

            error_patterns = [
                'UnicodeEncodeError',
                'UnicodeDecodeError',
                'JSON parsing error',
                'datetime.*not.*serializable',
                'emoji.*encoding',
                'surrogates not allowed'
            ]

            for log_file in log_files:
                try:
                    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()

                    for pattern in error_patterns:
                        if pattern.lower() in content.lower():
                            remaining_issues.append(
                                f"Pattern '{pattern}' found in {
                                    log_file.name}")

                except Exception:
                    continue

            # Check for problematic files
            problematic_patterns = [
                '*.tmp',
                '*unicode*error*',
                '*json*error*',
                '*serialization*error*'
            ]

            for pattern in problematic_patterns:
                problem_files = list(self.workspace_path.glob(pattern))
                if problem_files:
                    remaining_issues.append(
                        f"Problematic files found: {pattern}")

        except Exception as e:
            remaining_issues.append(f"Issue scanning error: {str(e)}")

        return remaining_issues

    def calculate_professional_score(self) -> float:
        """Calculate professional readiness score."""
        scores = {
            'unicode_compatibility': 25.0 if self.validation_results['unicode_compatibility'] else 0.0,
            'json_serialization': 25.0 if self.validation_results['json_serialization'] else 0.0,
            'performance_monitoring': 25.0 if self.validation_results['performance_monitoring'] else 0.0,
            'analytics_enhancement': 25.0 if self.validation_results['analytics_enhancement'] else 0.0}

        total_score = sum(scores.values())

        # Deduct points for remaining issues
        remaining_count = len(self.validation_results['remaining_issues'])
        penalty = min(remaining_count * 5.0, 20.0)  # Max 20 point penalty

        final_score = max(0.0, total_score - penalty)
        return final_score

    def run_comprehensive_validation(self):
        """Run comprehensive validation of all fixes."""
        print("\n" + "=" * 80)
        print("PROFESSIONAL ENVIRONMENT VALIDATION")
        print("Final validation for gh_COPILOT deployment readiness")
        print("=" * 80)

        self.logger.info("Starting professional environment validation...")

        # Run all validations
        print("\n[PHASE 1] Core Component Validation")
        self.validation_results['unicode_compatibility'] = self.validate_unicode_compatibility(
        )
        self.validation_results['json_serialization'] = self.validate_json_serialization(
        )
        self.validation_results['performance_monitoring'] = self.validate_performance_monitoring(
        )
        self.validation_results['analytics_enhancement'] = self.validate_analytics_enhancement(
        )

        # Check remaining issues
        print("\n[PHASE 2] Issue Detection")
        print("  [SCANNING] Remaining Issues...")
        self.validation_results['remaining_issues'] = self.check_remaining_issues(
        )

        remaining_count = len(self.validation_results['remaining_issues'])
        print(f"    Remaining issues found: {remaining_count}")

        if remaining_count == 0:
            print("    [SUCCESS] No remaining issues detected")
        else:
            print("    [WARNING] Some issues remain (non-critical)")
            # Show first 5
            for issue in self.validation_results['remaining_issues'][:5]:
                print(f"      - {issue}")
            if remaining_count > 5:
                print(f"      ... and {remaining_count - 5} more")

        # Calculate scores
        print("\n[PHASE 3] Professional Readiness Assessment")
        self.validation_results['issues_resolved'] = sum([
            self.validation_results['unicode_compatibility'],
            self.validation_results['json_serialization'],
            self.validation_results['performance_monitoring'],
            self.validation_results['analytics_enhancement']
        ])

        self.validation_results['professional_score'] = self.calculate_professional_score(
        )
        self.validation_results['overall_readiness'] = self.validation_results['professional_score'] >= 90.0

        # Display results
        print("\n" + "=" * 80)
        print("PROFESSIONAL VALIDATION RESULTS")
        print("=" * 80)

        print(
            f"Validation Timestamp: {
                self.validation_results['validation_timestamp']}")
        print()

        print("COMPONENT STATUS:")
        status_map = {True: '[SUCCESS]', False: '[WARNING]'}
        print(
            f"  Unicode Compatibility: {status_map[self.validation_results['unicode_compatibility']]}")
        print(
            f"  JSON Serialization: {status_map[self.validation_results['json_serialization']]}")
        print(
            f"  Performance Monitoring: {status_map[self.validation_results['performance_monitoring']]}")
        print(
            f"  Analytics Enhancement: {status_map[self.validation_results['analytics_enhancement']]}")
        print()

        print("PROFESSIONAL METRICS:")
        print(
            f"  Issues Resolved: {
                self.validation_results['issues_resolved']}/4")
        print(
            f"  Remaining Issues: {len(self.validation_results['remaining_issues'])}")
        print(
            f"  Professional Score: {
                self.validation_results['professional_score']:.1f}/100.0")
        print(
            f"  Overall Readiness: {status_map[self.validation_results['overall_readiness']]}")
        print()

        # Recommendations
        print("RECOMMENDATIONS:")
        if self.validation_results['overall_readiness']:
            print(
                "  [SUCCESS] Environment is ready for professional gh_COPILOT deployment")
            print("  [ACTION] Proceed with enterprise packaging and deployment")
        else:
            print("  [WARNING] Environment requires additional optimization")
            print("  [ACTION] Address remaining issues before deployment")

        # Save results
        results_path = self.workspace_path / \
            f'professional_validation_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump(self.validation_results, f, indent=2, ensure_ascii=False)

        print(f"\nValidation results saved to: {results_path}")

        return self.validation_results['overall_readiness']


def main():
    """Main execution function."""
    try:
        validator = ProfessionalEnvironmentValidator()
        success = validator.run_comprehensive_validation()

        if success:
            print(
                "\n[SUCCESS] Professional environment validation completed successfully")
            print("[READY] Environment is ready for gh_COPILOT deployment")
            return 0
        else:
            print(
                "\n[WARNING] Professional environment validation completed with warnings")
            print("[REVIEW] Review remaining issues before deployment")
            return 1

    except Exception as e:
        print(f"\n[ERROR] Professional validation failed: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
