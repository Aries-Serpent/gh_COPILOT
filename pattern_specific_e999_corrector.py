#!/usr/bin/env python3
"""
🎯 Pattern-Specific E999 Critical Error Corrector
=================================================
Specialized corrector for common E999 syntax error patterns observed
in the codebase, with focused pattern matching and surgical fixes.
"""

import os
import re
import logging
import sqlite3
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import shutil

# Enhanced logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PatternSpecificE999Corrector:
    """Pattern-specific E999 syntax error corrector with surgical precision."""

    def __init__(self, workspace_path: str = "."):
        self.workspace_path = Path(workspace_path)
        self.db_path = self.workspace_path / "databases" / "analytics.db"
        self.fixes_applied = 0
        self.patterns_fixed = {}

        # Common E999 patterns we've identified
        self.fix_patterns = [
            # Pattern 1: Unmatched closing parenthesis
            {
                'name': 'unmatched_closing_paren',
                'pattern': r'(\w+\s*=\s*\w+\.\w+\(\)\s*\n)([^(]+\n)\)',
                'fix': lambda m: f"{m.group(1).rstrip()}\n{m.group(2).rstrip()}\n)",
                'description': 'Fix unmatched closing parenthesis'
            },
            # Pattern 2: Missing opening parenthesis
            {
                'name': 'missing_opening_paren',
                'pattern': r'(\w+\.\w+)\(\)\s*\n([^(]+?)(\))',
                'fix': lambda m: f"{m.group(1)}(\n{m.group(2).strip()}\n{m.group(3)}",
                'description': 'Fix missing opening parenthesis'
            },
            # Pattern 3: Bracket/parenthesis mismatch
            {
                'name': 'bracket_paren_mismatch',
                'pattern': r'(\w+\s*=\s*\[)\s*([^[\]]*?)(\]?\s*\))',
                'fix': lambda m: f"{m.group(1)}\n    {m.group(2).strip()}\n]",
                'description': 'Fix bracket/parenthesis mismatch'
            },
            # Pattern 4: ValidationCheckpoint bracket issues
            {
                'name': 'validation_checkpoint_brackets',
                'pattern': r'ValidationCheckpoint\(\]',
                'fix': lambda m: 'ValidationCheckpoint(',
                'description': 'Fix ValidationCheckpoint bracket issues'
            },
            # Pattern 5: Unterminated string literals
            {
                'name': 'unterminated_string',
                'pattern': r"(['\"])((?:[^'\"\\]|\\.)*)(?!['\"])",
                'fix': lambda m: f"{m.group(1)}{m.group(2)}{m.group(1)}",
                'description': 'Fix unterminated string literals'
            }
        ]

    def backup_file(self, file_path: Path) -> Path:
        """Create backup of file before modification."""
        backup_dir = self.workspace_path / "backups" / f"pattern_fixes_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_dir.mkdir(parents=True, exist_ok=True)

        # Preserve directory structure
        rel_path = file_path.relative_to(self.workspace_path)
        backup_file = backup_dir / rel_path
        backup_file.parent.mkdir(parents=True, exist_ok=True)

        shutil.copy2(file_path, backup_file)
        return backup_file

    def apply_pattern_fixes(self, file_path: Path) -> int:
        """Apply pattern-specific fixes to a file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()

            content = original_content
            fixes_in_file = 0

            for pattern_info in self.fix_patterns:
                pattern = pattern_info['pattern']
                fix_func = pattern_info['fix']
                name = pattern_info['name']

                if isinstance(fix_func, str):
                    # Simple string replacement
                    if re.search(pattern, content):
                        content = re.sub(pattern, fix_func, content)
                        fixes_in_file += 1
                        self.patterns_fixed[name] = self.patterns_fixed.get(name, 0) + 1
                        logger.info(f"Applied {name} fix in {file_path}")
                else:
                    # Function-based replacement
                    matches = list(re.finditer(pattern, content))
                    if matches:
                        # Apply fixes in reverse order to maintain positions
                        for match in reversed(matches):
                            replacement = fix_func(match)
                            content = content[:match.start()] + replacement + content[match.end():]
                            fixes_in_file += 1
                            self.patterns_fixed[name] = self.patterns_fixed.get(name, 0) + 1
                            logger.info(f"Applied {name} fix in {file_path}")

            # Only write if changes were made
            if fixes_in_file > 0:
                # Create backup before modifying
                self.backup_file(file_path)

                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)

                logger.info(f"Applied {fixes_in_file} pattern fixes to {file_path}")

            return fixes_in_file

        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            return 0

    def get_e999_files(self) -> List[Path]:
        """Get list of files with E999 errors."""
        try:
            result = subprocess.run([
                'flake8', '--exclude=backups,__pycache__,.git', '--select=E999',
                '--format=%(path)s', '.'
            ], capture_output=True, text=True, cwd=self.workspace_path)

            files = []
            for line in result.stdout.strip().split('\n'):
                if line and line.endswith('.py'):
                    file_path = Path(line)
                    if file_path.exists():
                        files.append(file_path)

            return list(set(files))  # Remove duplicates

        except Exception as e:
            logger.error(f"Error getting E999 files: {e}")
            return []

    def run_pattern_corrections(self):
        """Run pattern-specific corrections on all E999 files."""
        logger.info("🎯 PATTERN-SPECIFIC E999 CORRECTOR STARTING")
        logger.info("=" * 50)

        e999_files = self.get_e999_files()
        logger.info(f"Found {len(e999_files)} files with E999 errors")

        for file_path in e999_files:
            fixes = self.apply_pattern_fixes(file_path)
            self.fixes_applied += fixes

        logger.info("=" * 50)
        logger.info(f"PATTERN CORRECTION SUMMARY")
        logger.info(f"Files processed: {len(e999_files)}")
        logger.info(f"Total fixes applied: {self.fixes_applied}")
        logger.info(f"Patterns fixed: {self.patterns_fixed}")
        logger.info("=" * 50)

        return self.fixes_applied > 0


def main():
    """Main execution function."""
    corrector = PatternSpecificE999Corrector()
    success = corrector.run_pattern_corrections()

    if success:
        print("✅ Pattern-specific corrections completed successfully!")
    else:
        print("⚠️ No pattern fixes were applied.")

if __name__ == "__main__":
    main()
