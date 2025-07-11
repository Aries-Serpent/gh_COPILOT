#!/usr/bin/env python3
"""
TARGETED CRITICAL ERROR FIXER
================================
Focused script to fix specific critical error patterns identified in the analysis.
Based on the comprehensive error analysis methodology provided.
"""

import os
import re
import shutil
from pathlib import Path
from datetime import datetime


class TargetedCriticalErrorFixer:
    """Targeted fixer for specific critical error patterns"""

    def __init__(self, workspace_root: str):
        self.workspace_root = Path(workspace_root)
        self.backup_dir = self.workspace_root / "backups" / f"targeted_fixes_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # Common critical error patterns and their fixes
        self.critical_fixes = {
            'bracket_mismatch_1': {
                'pattern': r"closing parenthesis '\]' does not match opening parenthesis '\('",
                'action': 'replace_bracket',
                'replace_from': ']',
                'replace_to': ')'
            },
            'bracket_mismatch_2': {
                'pattern': r"closing parenthesis '\)' does not match opening parenthesis '\['",
                'action': 'replace_bracket',
                'replace_from': ')',
                'replace_to': ']'
            },
            'bracket_mismatch_3': {
                'pattern': r"closing parenthesis '\}' does not match opening parenthesis '\[' on line \d+",
                'action': 'replace_bracket',
                'replace_from': '}',
                'replace_to': ']'
            },
            'bracket_mismatch_4': {
                'pattern': r"closing parenthesis '\]' does not match opening parenthesis '\{' on line \d+",
                'action': 'replace_bracket',
                'replace_from': ']',
                'replace_to': '}'
            },
            'unmatched_closing': {
                'pattern': r"unmatched '(\]|\)|\})'",
                'action': 'remove_unmatched'
            },
            'unexpected_indent': {
                'pattern': r"IndentationError: unexpected indent",
                'action': 'fix_indent'
            }
        }

    def fix_file(self, file_path: str, error_line: int, error_message: str) -> bool:
        """Fix a specific error in a file"""
        try:
            # Create backup
            backup_path = self.backup_dir / Path(file_path).name
            if not backup_path.exists():
                shutil.copy2(file_path, backup_path)

            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            if error_line > len(lines):
                return False

            # Apply appropriate fix based on error pattern
            for fix_name, fix_config in self.critical_fixes.items():
                if re.search(fix_config['pattern'], error_message):
                    fixed = self._apply_fix(
                                            lines,
                                            error_line - 1,
                                            fix_config,
                                            error_message
                    fixed = self._apply_fix(lines, error_line -)
                    if fixed:
                        # Write the fixed content back
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.writelines(lines)
                        print(f"✓ Fixed {fix_name} in {file_path}:{error_line}")
                        return True

            return False

        except Exception as e:
            print(f"✗ Error fixing {file_path}: {e}")
            return False

    def _apply_fix(
                   self,
                   lines: list,
                   line_idx: int,
                   fix_config: dict,
                   error_message: str) -> bool
    def _apply_fix(sel)
        """Apply a specific fix to the lines"""
        if line_idx >= len(lines):
            return False

        line = lines[line_idx]

        if fix_config['action'] == 'replace_bracket':
            # Replace mismatched bracket
            old_char = fix_config['replace_from']
            new_char = fix_config['replace_to']

            # Find the rightmost occurrence of the old character
            if old_char in line:
                # Replace from right to left to handle the closing bracket
                pos = line.rfind(old_char)
                if pos != -1:
                    lines[line_idx] = line[:pos] + new_char + line[pos+1:]
                    return True

        elif fix_config['action'] == 'remove_unmatched':
            # Remove unmatched closing brackets
            unmatched_chars = [']', ')', '}']
            for char in unmatched_chars:
                if char in line:
                    # Count opening vs closing to see if there's truly an unmatched one
                    opening_map = {'[': ']', '(': ')', '{': '}'}
                    closing_map = {v: k for k, v in opening_map.items()}

                    if char in closing_map:
                        opening_char = closing_map[char]
                        open_count = line.count(opening_char)
                        close_count = line.count(char)

                        if close_count > open_count:
                            # Remove the extra closing bracket
                            pos = line.rfind(char)
                            lines[line_idx] = line[:pos] + line[pos+1:]
                            return True

        elif fix_config['action'] == 'fix_indent':
            # Fix unexpected indentation
            if line.strip() and (line.startswith('    ') or line.startswith('\t')):
                # Check if the previous line suggests this should be indented
                if line_idx > 0:
                    prev_line = lines[line_idx - 1].strip()
                    if not prev_line.endswith(':') and not prev_line.endswith('\\'):
                        # Remove the indentation
                        lines[line_idx] = line.lstrip()
                        return True

        return False


def main():
    """Main function to run targeted fixes"""
    print("TARGETED CRITICAL ERROR FIXER")
    print("=" * 40)

    workspace = os.getcwd()
    fixer = TargetedCriticalErrorFixer(workspace)

    # Common critical error files and their known issues
    critical_fixes_needed = [
        (
         'database_consolidation_migration.py',
         127,
         "closing parenthesis ')' does not match opening parenthesis '[' on line 80")
        ('databa)
        ('database_sync_scheduler.py', 17, "unmatched ')'"),
        ('session_protocol_validator.py', 27, "'[' was never closed"),
        ('physics_optimization_engine.py', 54, "unmatched ')'"),
    ]

    fixed_count = 0
    total_attempts = 0

    for file_path, line_num, error_msg in critical_fixes_needed:
        full_path = os.path.join(workspace, file_path)
        if os.path.exists(full_path):
            total_attempts += 1
            if fixer.fix_file(full_path, line_num, error_msg):
                fixed_count += 1

    print(f"\nTargeted fixes completed: {fixed_count}/{total_attempts} successful")
    print("=" * 40)

if __name__ == "__main__":
    main()
