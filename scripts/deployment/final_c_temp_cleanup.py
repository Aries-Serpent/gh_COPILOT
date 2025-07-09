#!/usr/bin/env python3
"""
Final E:\\gh_COPILOT	emp Cleanup Script - Enterprise Session Integrity Validator
CLEAN VERSION - NO UNICODE/EMOJI CHARACTERS
"""

import os
import re
import json
import logging
from pathlib import Path
from datetime import datetime
import subprocess

# Clean logging setup - NO UNICODE
logging.basicConfig(]
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('final_c_temp_cleanup.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class FinalCTempCleanup:
    def __init__(self):
        self.workspace_root = Path("E:/gh_COPILOT")
        self.session_id = f"FINAL_CLEANUP_{int(datetime.now().timestamp())}"
        self.violations_fixed = 0
        self.files_processed = 0

        logger.info("FINAL C:TEMP CLEANUP INITIALIZED")
        logger.info(f"Session ID: {self.session_id}")
        logger.info(f"Workspace Root: {self.workspace_root}")

    def find_c_temp_violations(self):
        """Find all E:\\gh_COPILOT	emp violations in Python files"""
        violations = [
        python_files = list(self.workspace_root.glob("*.py"))

        logger.info(
            f"Scanning {len(python_files)} Python files for C:Temp violations")

        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Look for various E:\gh_COPILOT	emp patterns
                patterns = [
                    r'C:\\[Tt]emp',
                    r'C:/[Tt]emp',
                    r'"C:\\\\temp"',
                    r"'C:\\\\temp'",
                    r'"E:\gh_COPILOT	emp"',
                    r"'E:\gh_COPILOT	emp'",
                    r'tempfile\.gettempdir\(\)',
                    r'os\.environ\.get\(["\']TEMP["\']',
                    r'os\.environ\.get\(["\']TMP["\']'
                ]

                found_violations = [
                lines = content.split('\n')

                for i, line in enumerate(lines, 1):
                    for pattern in patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            found_violations.append(]
                                'line_content': line.strip(),
                                'pattern': pattern
                            })

                if found_violations:
                    violations.append(]
                        'file': str(file_path),
                        'violations': found_violations
                    })
                    logger.error(f"C:TEMP VIOLATION FOUND: {file_path}")

            except Exception as e:
                logger.error(f"Error scanning {file_path}: {e}")

        return violations

    def fix_c_temp_violations(self, violations):
        """Fix all E:\\gh_COPILOT	emp violations by replacing with workspace-relative paths"""
        fixed_count = 0

        for file_violation in violations:
            file_path = Path(file_violation['file'])

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                original_content = content

                # Replace various E:\gh_COPILOT	emp patterns with workspace-relative paths
                replacements = [
                    (r'C:\\[Tt]emp', str(self.workspace_root / "temp")),
                    (r'C:/[Tt]emp', str(self.workspace_root / "temp")),
                    (r'"C:\\\\temp"', f'"{self.workspace_root / "temp"}"'),
                    (r"'C:\\\\temp'", f"'{self.workspace_root / 'temp'}'"),
                    (]
                     f'"{self.workspace_root / "temp"}"'),
                    (]
                     f"'{self.workspace_root / 'temp'}'"),
                    (r'tempfile\.gettempdir\(\)',
                     f'"{self.workspace_root / "temp"}"'),
                    (r'os\.environ\.get\(["\']TEMP["\'][^)]*\)',
                     f'"{self.workspace_root / "temp"}"'),
                    (r'os\.environ\.get\(["\']TMP["\'][^)]*\)',
                     f'"{self.workspace_root / "temp"}"')
                ]

                for pattern, replacement in replacements:
                    content = re.sub(]
                                     content, flags=re.IGNORECASE)

                if content != original_content:
                    # Create backup before modifying
                    backup_path = file_path.with_suffix(]
                        f'.backup_{self.session_id}')
                    with open(backup_path, 'w', encoding='utf-8') as f:
                        f.write(original_content)

                    # Write fixed content
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)

                    fixed_count += 1
                    logger.info(f"FIXED C:TEMP VIOLATIONS: {file_path}")
                    logger.info(f"Backup created: {backup_path}")

            except Exception as e:
                logger.error(f"Error fixing {file_path}: {e}")

        return fixed_count

    def ensure_temp_directory(self):
        """Ensure workspace temp directory exists"""
        temp_dir = self.workspace_root / "temp"
        temp_dir.mkdir(exist_ok=True)
        logger.info(f"Ensured temp directory exists: {temp_dir}")
        return temp_dir

    def validate_fixes(self):
        """Validate that all E:\\gh_COPILOT	emp violations have been fixed"""
        violations = self.find_c_temp_violations()

        if violations:
            logger.error(
                f"VALIDATION FAILED: {len(violations)} files still have C:Temp violations")
            for violation in violations:
                logger.error(f"  - {violation['file']}")
            return False
        else:
            logger.info("VALIDATION PASSED: No C:Temp violations found")
            return True

    def run_cleanup(self):
        """Run the complete cleanup process"""
        logger.info("STARTING FINAL C:TEMP CLEANUP PROCESS")

        # Step 1: Find violations
        logger.info("Phase 1: Finding C:Temp violations")
        violations = self.find_c_temp_violations()

        if not violations:
            logger.info("NO C:TEMP VIOLATIONS FOUND - CLEANUP NOT NEEDED")
            return {}

        logger.info(f"Found {len(violations)} files with C:Temp violations")

        # Step 2: Ensure temp directory exists
        logger.info("Phase 2: Ensuring workspace temp directory exists")
        self.ensure_temp_directory()

        # Step 3: Fix violations
        logger.info("Phase 3: Fixing C:Temp violations")
        fixed_count = self.fix_c_temp_violations(violations)

        # Step 4: Validate fixes
        logger.info("Phase 4: Validating fixes")
        validation_passed = self.validate_fixes()

        result = {
            'violations_found': len(violations),
            'violations_fixed': fixed_count,
            'validation_passed': validation_passed,
            'session_id': self.session_id,
            'timestamp': datetime.now().isoformat()
        }

        # Save results
        results_file = self.workspace_root / \
            f"final_c_temp_cleanup_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)

        logger.info(f"Results saved to: {results_file}")

        if validation_passed:
            logger.info("FINAL C:TEMP CLEANUP: SUCCESS")
        else:
            logger.error("FINAL C:TEMP CLEANUP: FAILED")

        return result


def main():
    """Main execution function"""
    try:
        cleanup = FinalCTempCleanup()
        result = cleanup.run_cleanup()

        if result['status'] == 'SUCCESS':
            logger.info("CLEANUP COMPLETED SUCCESSFULLY")
            return 0
        else:
            logger.error("CLEANUP FAILED")
            return 1

    except Exception as e:
        logger.error(f"FATAL ERROR: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
