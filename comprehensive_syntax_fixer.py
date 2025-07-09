#!/usr/bin/env python3
"""
🔧 COMPREHENSIVE SYNTAX FIXER v1.0
==================================
Systematically fix common syntax errors across the codebase

Focus on:
- cursor.execute( → cursor.execute(
- logging.info( → logging.info(
- print( → print(
- Missing closing brackets
- Malformed lists and dictionaries
"""

import os
import re
import sys
import json
from pathlib import Path
from typing import List, Dict, Any
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('syntax_fixer.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ComprehensiveSyntaxFixer:
    """Comprehensive syntax error correction system"""

    def __init__(self, workspace_path: str = "e:\\gh_COPILOT"):
        self.workspace_path = Path(workspace_path)
        self.fixes_applied = 0
        self.files_processed = 0
        self.error_patterns = [
            # Function call bracket fixes
            (r'logging\.info\(\]', 'logging.info('),
            (r'logging\.error\(\]', 'logging.error('),
            (r'logging\.warning\(\]', 'logging.warning('),
            (r'logger\.info\(\]', 'logger.info('),
            (r'logger\.error\(\]', 'logger.error('),
            (r'logger\.warning\(\]', 'logger.warning('),
            (r'print\(\]', 'print('),
            (r'cursor\.execute\(\]', 'cursor.execute('),

            # Dictionary/list bracket fixes
            (r'= \{\]', '= {'),
            (r'= \[\]', '= ['),
            (r'\{\]\s*}', '{}'),
            (r'\[\]\s*\]', '[]'),

            # Common malformed patterns
            (r'handlers\s*=\s*\[\]', 'handlers=['),
            (r'@dataclass', '@dataclass'),

            # Specific problematic patterns
            (r'VISUAL_INDICATORS\s*=\s*\{\]', 'VISUAL_INDICATORS = {'),
            (r'FORBIDDEN_PATTERNS\s*=\s*\[\]', 'FORBIDDEN_PATTERNS = ['),
        ]

    def fix_file(self, file_path: Path) -> int:
        """Fix syntax errors in a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            original_content = content
            fixes_count = 0

            # Apply all error pattern fixes
            for pattern, replacement in self.error_patterns:
                matches = re.findall(pattern, content)
                if matches:
                    content = re.sub(pattern, replacement, content)
                    fixes_count += len(matches)

            # Additional specific fixes
            content = self._fix_specific_patterns(content, file_path)

            # Only write if changes were made
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger.info(f"Applied {fixes_count} fixes to {file_path}")
                return fixes_count

            return 0

        except Exception as e:
            logger.error(f"Error fixing {file_path}: {e}")
            return 0

    def _fix_specific_patterns(self, content: str, file_path: Path) -> str:
        """Apply specific pattern fixes"""

        # Fix malformed logging statements
        content = re.sub(
            r'logging\.info\(\]\s*\n\s*f"([^"]+)"\)',
            r'logging.info(f"\1")',
            content,
            flags=re.MULTILINE
        )

        content = re.sub(
            r'logging\.error\(\]\s*\n\s*f"([^"]+)"\)',
            r'logging.error(f"\1")',
            content,
            flags=re.MULTILINE
        )

        # Fix malformed print statements
        content = re.sub(
            r'print\(\]\s*\n\s*f"([^"]+)"\)',
            r'print(f"\1")',
            content,
            flags=re.MULTILINE
        )

        # Fix malformed cursor.execute statements
        content = re.sub(
            r'cursor\.execute\(\]\s*\n\s*"([^"]+)"',
            r'cursor.execute("\1"',
            content,
            flags=re.MULTILINE
        )

        # Fix malformed dictionary assignments
        if 'VISUAL_INDICATORS = {' in content:
            content = content.replace(
                'VISUAL_INDICATORS = {',
                'VISUAL_INDICATORS = {'
            )

        # Fix malformed list assignments
        if 'FORBIDDEN_PATTERNS = [' in content and 'r\'C:\\' in content:
            content = re.sub(
                r'FORBIDDEN_PATTERNS = \[\]\s*\n\s*r\'([^\']+)\'',
                r'FORBIDDEN_PATTERNS = [\n        r\'\1\'',
                content
            )

        return content

    def fix_codebase(self) -> Dict[str, Any]:
        """Fix syntax errors across the entire codebase"""
        logger.info("Starting comprehensive syntax fixing...")

        start_time = datetime.now()

        # Find all Python files
        python_files = list(self.workspace_path.rglob("*.py"))

        # Exclude certain directories
        excluded_patterns = [
            "*/__pycache__/*",
            "*/venv/*",
            "*/env/*",
            "*/.git/*",
            "*/.pytest_cache/*"
        ]

        python_files = [
            f for f in python_files
            if not any(f.match(pattern) for pattern in excluded_patterns)
        ]

        logger.info(f"Found {len(python_files)} Python files to process")

        # Process each file
        for file_path in python_files:
            try:
                fixes = self.fix_file(file_path)
                self.fixes_applied += fixes
                self.files_processed += 1

                if self.files_processed % 50 == 0:
                    logger.info(
                        f"Processed {
                            self.files_processed} files so far.")

            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}")
                continue

        duration = (datetime.now() - start_time).total_seconds()

        results = {
            "files_processed": self.files_processed,
            "fixes_applied": self.fixes_applied,
            "duration_seconds": duration,
            "timestamp": datetime.now().isoformat()
        }

        return results


def main():
    """Main execution function"""
    print("COMPREHENSIVE SYNTAX FIXER v1.0")
    print("==================================")
    print("Fixing common syntax errors across the codebase...")

    try:
        fixer = ComprehensiveSyntaxFixer()
        results = fixer.fix_codebase()

        print(f"\nSYNTAX FIXING COMPLETE!")
        print(f"Files Processed: {results['files_processed']}")
        print(f"Fixes Applied: {results['fixes_applied']}")
        print(f"Duration: {results['duration_seconds']:.2f} seconds")

        # Save results
        with open('syntax_fixes_report.json', 'w') as f:
            json.dump(results, f, indent=2)

        print(f"Report saved to: syntax_fixes_report.json")

        return True

    except Exception as e:
        print(f"Syntax fixing failed: {e}")
        logger.error(f"Syntax fixing failed: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
