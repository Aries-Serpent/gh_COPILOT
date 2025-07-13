#!/usr/bin/env python3
"""
🔍 VIOLATION DIAGNOSTIC PROCESSOR
Database Violation Analysis and Status Investigation

Author: Enterprise Violation Processing System
Date: July 13, 2025
Status: DIAGNOSTIC MODE
"""

import sys
import sqlite3
import logging
from pathlib import Path
from typing import Dict, Any

# Configure diagnostic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('violation_diagnostic.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class ViolationDiagnosticProcessor:
    """🔍 Diagnostic processor for violation database analysis"""

    def __init__(self, workspace_path: str = "e:/gh_COPILOT"):
        self.workspace_path = Path(workspace_path)
        self.database_path = self.workspace_path / "databases" / "flake8_violations.db"

        logger.info("🔍 VIOLATION DIAGNOSTIC PROCESSOR INITIALIZED")
        logger.info(f"Database: {self.database_path}")

    def analyze_violation_status(self) -> Dict[str, Any]:
        """📊 Analyze violation status in database"""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()

                # Get overall violation counts by status
                cursor.execute("""
                    SELECT status, COUNT(*) as count
                    FROM violations
                    GROUP BY status
                    ORDER BY count DESC
                """)
                status_counts = dict(cursor.fetchall())

                # Get violation counts by error code
                cursor.execute("""
                    SELECT error_code, COUNT(*) as count
                    FROM violations
                    WHERE status = 'pending'
                    GROUP BY error_code
                    ORDER BY count DESC
                    LIMIT 10
                """)
                pending_by_code = dict(cursor.fetchall())

                # Get sample pending violations
                cursor.execute("""
                    SELECT id, file_path, line_number, error_code, message
                    FROM violations
                    WHERE status = 'pending' AND error_code IN ('W291', 'W293')
                    LIMIT 5
                """)
                sample_violations = cursor.fetchall()

                # Check if violations have actual content
                cursor.execute("""
                    SELECT file_path, COUNT(*) as count
                    FROM violations
                    WHERE status = 'pending' AND error_code IN ('W291', 'W293')
                    GROUP BY file_path
                    ORDER BY count DESC
                    LIMIT 5
                """)
                file_violations = cursor.fetchall()

                analysis = {
                    'status_counts': status_counts,
                    'pending_by_code': pending_by_code,
                    'sample_violations': sample_violations,
                    'file_violations': file_violations,
                    'total_pending': status_counts.get('pending', 0)
                }

                return analysis

        except Exception as e:
            logger.error(f"❌ Database analysis error: {e}")
            return {}

    def check_file_content(self, file_path: str, line_number: int) -> Dict[str, Any]:
        """📄 Check actual file content for violation"""
        try:
            if not Path(file_path).exists():
                return {'exists': False, 'error': 'File not found'}

            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            if line_number <= len(lines):
                line_content = lines[line_number - 1] if line_number > 0 else ""
                return {
                    'exists': True,
                    'line_content': repr(line_content),
                    'has_trailing_whitespace': line_content.rstrip() != line_content.rstrip('\n'),
                    'is_blank_with_whitespace': line_content.strip() == '' \
    and line_content.rstrip('\n') != '',
                    'total_lines': len(lines)
                }
            else:
                return {'exists': True,
                    'error': f'Line {line_number} out of range (file has {len(lines)} lines)'}

        except Exception as e:
            return {'exists': True, 'error': f'File read error: {e}'}

    def run_diagnostic(self):
        """🔍 Run comprehensive diagnostic"""
        logger.info("="*80)
        logger.info("🔍 VIOLATION DIAGNOSTIC ANALYSIS")
        logger.info("="*80)

        # Analyze database
        analysis = self.analyze_violation_status()

        print("\n📊 VIOLATION STATUS COUNTS:")
        for status, count in analysis.get('status_counts', {}).items():
            print(f"   {status}: {count}")

        print("\n📋 PENDING VIOLATIONS BY ERROR CODE:")
        for code, count in analysis.get('pending_by_code', {}).items():
            print(f"   {code}: {count}")

        print("\n📄 FILES WITH MOST PENDING VIOLATIONS:")
        for file_path, count in analysis.get('file_violations', []):
            print(f"   {Path(file_path).name}: {count} violations")

        print("\n🔍 SAMPLE VIOLATION ANALYSIS:")
        for violation in analysis.get('sample_violations', []):
            id, file_path, line_number, error_code, message = violation
            print(f"\n   Violation ID: {id}")
            print(f"   File: {Path(file_path).name}")
            print(f"   Line: {line_number}")
            print(f"   Code: {error_code}")
            print(f"   Message: {message}")

            # Check actual file content
            file_check = self.check_file_content(file_path, line_number)
            if file_check.get('exists'):
                if 'error' in file_check:
                    print(f"   Status: ❌ {file_check['error']}")
                else:
                    line_content = file_check['line_content']
                    print(f"   Line Content: {line_content}")

                    if error_code == 'W291':
                        has_trailing = file_check.get('has_trailing_whitespace', False)
                        print(f"   Has trailing whitespace: {has_trailing}")
                        if not has_trailing:
                            print("   Status: ✅ Already fixed (no trailing whitespace)")
                        else:
                            print("   Status: ⚠️ Still needs fixing")

                    elif error_code == 'W293':
                        has_whitespace_blank = file_check.get('is_blank_with_whitespace', False)
                        print(f"   Is blank line with whitespace: {has_whitespace_blank}")
                        if not has_whitespace_blank:
                            print("   Status: ✅ Already fixed (blank line is clean)")
                        else:
                            print("   Status: ⚠️ Still needs fixing")
            else:
                print("   Status: ❌ File not found")

        # Summary
        total_pending = analysis.get('total_pending', 0)
        w291_count = analysis.get('pending_by_code', {}).get('W291', 0)
        w293_count = analysis.get('pending_by_code', {}).get('W293', 0)

        print("\n📈 DIAGNOSTIC SUMMARY:")
        print(f"   Total pending violations: {total_pending}")
        print(f"   W291 (trailing whitespace): {w291_count}")
        print(f"   W293 (blank line whitespace): {w293_count}")
        print(f"   Target violations available: {w291_count + w293_count}")

        if total_pending == 0:
            print("\n🎉 All violations have been processed!")
        elif w291_count == 0 and w293_count == 0:
            print("\n✅ All W291/W293 violations have been processed!")
            print("   Remaining violations are other types")
        else:
            print("\n⚠️ Target violations still pending - may need actual fixing")


def main():
    """🔍 Main diagnostic execution"""
    try:
        processor = ViolationDiagnosticProcessor()
        processor.run_diagnostic()

    except Exception as e:
        logger.error(f"❌ Diagnostic failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
