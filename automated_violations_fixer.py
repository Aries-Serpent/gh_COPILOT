#!/usr/bin/env python3
"""
🔧 AUTOMATED VIOLATIONS FIXER
Enterprise-grade automated fix system for 12,844+ Flake8 violations
"""

import sqlite3
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import logging
from tqdm import tqdm
import shutil

# MANDATORY: Anti-recursion validation


def validate_workspace_integrity() -> bool:
    """🛡️ CRITICAL: Validate workspace integrity before operations"""
    workspace_root = Path(os.getcwd())

    # Check for recursive patterns
    forbidden_patterns = ['*backup*', '*_backup_*', 'backups', '*temp*']
    violations = []

    for pattern in forbidden_patterns:
        for folder in workspace_root.rglob(pattern):
            if folder.is_dir() and folder != workspace_root:
                violations.append(str(folder))

    if violations:
        for violation in violations:
            print(f"🚨 RECURSIVE VIOLATION: {violation}")
        raise RuntimeError("CRITICAL: Recursive violations prevent execution")

    return True


@dataclass
class FixResult:
    """🔧 Fix result tracking"""
    violation_id: int
    file_path: str
    line_number: int
    error_code: str
    original_line: str
    fixed_line: str
    success: bool
    error_message: Optional[str] = None


class AutomatedViolationsFixer:
    """🔧 Enterprise-grade automated violations fixer"""

    def __init__(self, workspace_path: str = "e:/gh_COPILOT"):
        # CRITICAL: Validate workspace integrity
        validate_workspace_integrity()

        self.workspace_path = Path(workspace_path)
        self.database_path = self.workspace_path / "databases" / "flake8_violations.db"
        self.backup_dir = Path("E:/temp/gh_COPILOT_Backups") / \
                               "automated_fixes" / datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # Initialize logging
        self.setup_logging()

        # Define fixable violation types with their fix functions
        self.fixers = {
            'W293': self._fix_w293_blank_line_whitespace,
            'E302': self._fix_e302_expected_blank_lines,
            'E305': self._fix_e305_expected_blank_lines,
            'F401': self._fix_f401_unused_import,
            'E501': self._fix_e501_line_too_long,
            'E303': self._fix_e303_too_many_blank_lines,
            'W291': self._fix_w291_trailing_whitespace,
            'W292': self._fix_w292_no_newline_at_eof,
            'E301': self._fix_e301_expected_blank_line,
            'E261': self._fix_e261_inline_comment_spacing
        }

        print("🔧 AUTOMATED VIOLATIONS FIXER INITIALIZED")
        print(f"Database: {self.database_path}")
        print(f"Backup: {self.backup_dir}")
        print(f"Fixable Types: {len(self.fixers)} violation types")

    def setup_logging(self):
        """📋 Setup enterprise logging"""
        log_dir = self.workspace_path / "logs"
        log_dir.mkdir(exist_ok=True)

        # Create file handler with UTF-8 encoding
        file_handler = logging.FileHandler(
            log_dir / "automated_violations_fixer.log", 
            encoding='utf-8'
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))

        # Setup logger
        self.logger = logging.getLogger("automated_violations_fixer")
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(file_handler)

    def get_fixable_violations(self) -> List[Tuple]:
        """📊 Get violations that can be automatically fixed"""
        with sqlite3.connect(self.database_path) as conn:
            cursor = conn.cursor()

            fixable_codes = list(self.fixers.keys())
            placeholders = ','.join(['?' for _ in fixable_codes])

            cursor.execute(f"""
                SELECT id, file_path, line_number, column_number, error_code, message
                FROM violations 
                WHERE error_code IN ({placeholders})
                AND status = 'pending'
                ORDER BY file_path, line_number
            """, fixable_codes)

            return cursor.fetchall()

    def create_file_backup(self, file_path: str) -> str:
        """💾 Create backup of file before modification"""
        source_file = Path(file_path)
        if not source_file.exists():
            return ""

        # Create relative backup path
        relative_path = source_file.relative_to(self.workspace_path)
        backup_file = self.backup_dir / relative_path
        backup_file.parent.mkdir(parents=True, exist_ok=True)

        shutil.copy2(source_file, backup_file)
        return str(backup_file)

    def read_file_lines(self, file_path: str) -> List[str]:
        """📖 Read file lines with encoding detection"""
        try:
            # Try UTF-8 first
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.readlines()
        except UnicodeDecodeError:
            try:
                # Try with other encodings
                with open(file_path, 'r', encoding='latin-1') as f:
                    return f.readlines()
            except Exception:
                # Last resort - read as binary and decode with errors='replace'
                with open(file_path, 'rb') as f:
                    content = f.read().decode('utf-8', errors='replace')
                    return content.splitlines(keepends=True)

    def write_file_lines(self, file_path: str, lines: List[str]) -> bool:
        """✍️ Write file lines with proper encoding"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            return True
        except Exception as e:
            self.logger.error(f"Error writing file {file_path}: {e}")
            return False

    # Fix methods for specific violation types

    def _fix_w293_blank_line_whitespace(
        self, lines: List[str], line_num: int) -> Tuple[bool, str, str]:
        """🔧 Fix W293: blank line contains whitespace"""
        if line_num <= 0 or line_num > len(lines):
            return False, "", "Invalid line number"

        original_line = lines[line_num - 1]

        # Remove whitespace from blank lines
        if original_line.strip() == '':
            fixed_line = '\n' if original_line.endswith('\n') else ''
            lines[line_num - 1] = fixed_line
            return True, original_line.rstrip(), fixed_line.rstrip()

        return False, original_line, "Line not blank"

    def _fix_e302_expected_blank_lines(
        self, lines: List[str], line_num: int) -> Tuple[bool, str, str]:
        """🔧 Fix E302: expected 2 blank lines before function/class"""
        if line_num <= 2:
            return False, "", "Cannot add blank lines at file start"

        original_line = lines[line_num - 1]

        # Check if this is a function or class definition
        stripped = original_line.strip()
        if stripped.startswith('def ') or stripped.startswith('class '):
            # Count existing blank lines before
            blank_count = 0
            for i in range(line_num - 2, -1, -1):
                if lines[i].strip() == '':
                    blank_count += 1
                else:
                    break

            # Add blank lines to make it 2
            if blank_count < 2:
                lines_to_add = 2 - blank_count
                for _ in range(lines_to_add):
                    lines.insert(line_num - 1, '\n')
                return True, original_line.rstrip(), f"Added {lines_to_add} blank lines"

        return False, original_line, "Not a function/class definition"

    def _fix_e305_expected_blank_lines(
        self, lines: List[str], line_num: int) -> Tuple[bool, str, str]:
        """🔧 Fix E305: expected 2 blank lines after class/function"""
        if line_num >= len(lines):
            return False, "", "At end of file"

        original_line = lines[line_num - 1]

        # Look for function/class definitions ending
        if line_num > 1:
            prev_line = lines[line_num - 2].strip()
            if (prev_line.startswith('def ') or prev_line.startswith('class ') or 
                prev_line.endswith(':') and ('def ' in prev_line or 'class ' in prev_line)):

                # Add blank line after
                lines.insert(line_num, '\n')
                return True, original_line.rstrip(), "Added blank line"

        return False, original_line, "Not after function/class"

    def _fix_f401_unused_import(self, lines: List[str], line_num: int) -> Tuple[bool, str, str]:
        """🔧 Fix F401: unused import (conservative approach)"""
        if line_num <= 0 or line_num > len(lines):
            return False, "", "Invalid line number"

        original_line = lines[line_num - 1]
        stripped = original_line.strip()

        # Only remove simple unused imports (be conservative)
        if (stripped.startswith('import ') or stripped.startswith(
            'from ')) and not stripped.endswith('\\'):
            # Check if it's a safe import to remove (no side effects)
            safe_imports = [
    'os',
    'sys',
    're',
    'json',
    'datetime',
    'pathlib',
    'typing',
     'collections']

            import_name = ''
            if stripped.startswith('import '):
                import_name = stripped.split()[1].split('.')[0]
            elif stripped.startswith('from '):
                import_name = stripped.split()[1].split('.')[0]

            if import_name in safe_imports:
                # Comment out the import instead of removing
                lines[line_num -
     1] = f"# {original_line}" if not original_line.startswith('#') else original_line
                return True, original_line.rstrip(), f"# {original_line.rstrip()}"

        return False, original_line, "Not safe to remove"

    def _fix_e501_line_too_long(self, lines: List[str], line_num: int) -> Tuple[bool, str, str]:
        """🔧 Fix E501: line too long (basic cases only)"""
        if line_num <= 0 or line_num > len(lines):
            return False, "", "Invalid line number"

        original_line = lines[line_num - 1]

        # Only fix simple cases - long string literals
        if len(original_line) > 79 and '"' in original_line:
            # Try to break long string literals
            if original_line.count('"') >= 2:
                # Find string positions
                first_quote = original_line.find('"')
                last_quote = original_line.rfind('"')

                if last_quote > first_quote and last_quote - first_quote > 40:
                    # Split the string
                    before = original_line[:first_quote]
                    string_content = original_line[first_quote:last_quote+1]
                    after = original_line[last_quote+1:]

                    if len(string_content) > 40:
                        # Simple split at midpoint
                        mid = len(string_content) // 2
                        part1 = string_content[:mid] + '"'
                        part2 = '"' + string_content[mid+1:]

                        fixed_line = f"{before}{part1} \\\n{' ' * (len(before))}{part2}{after}"
                        lines[line_num - 1] = fixed_line
                        return True, original_line.rstrip(), "Split long string"

        return False, original_line, "Complex line - manual fix needed"

    def _fix_e303_too_many_blank_lines(
        self, lines: List[str], line_num: int) -> Tuple[bool, str, str]:
        """🔧 Fix E303: too many blank lines"""
        if line_num <= 0 or line_num > len(lines):
            return False, "", "Invalid line number"

        original_line = lines[line_num - 1]

        # Remove excess blank lines (keep max 2)
        if original_line.strip() == '':
            # Count consecutive blank lines
            blank_count = 0
            start_idx = line_num - 1

            # Count backwards
            for i in range(line_num - 1, -1, -1):
                if lines[i].strip() == '':
                    blank_count += 1
                    start_idx = i
                else:
                    break

            # Count forwards
            for i in range(line_num, len(lines)):
                if lines[i].strip() == '':
                    blank_count += 1
                else:
                    break

            # Remove excess (keep max 2)
            if blank_count > 2:
                excess = blank_count - 2
                # Remove from current position
                for _ in range(excess):
                    if line_num - 1 < len(lines) and lines[line_num - 1].strip() == '':
                        lines.pop(line_num - 1)
                return True, original_line.rstrip(), f"Removed {excess} excess blank lines"

        return False, original_line, "Not a blank line"

    def _fix_w291_trailing_whitespace(
        self, lines: List[str], line_num: int) -> Tuple[bool, str, str]:
        """🔧 Fix W291: trailing whitespace"""
        if line_num <= 0 or line_num > len(lines):
            return False, "", "Invalid line number"

        original_line = lines[line_num - 1]

        # Remove trailing whitespace
        fixed_line = original_line.rstrip() + '\n' if original_line.endswith('\n') else original_line.rstrip()
        if fixed_line != original_line:
            lines[line_num - 1] = fixed_line
            return True, original_line.rstrip(), fixed_line.rstrip()

        return False, original_line, "No trailing whitespace"

    def _fix_w292_no_newline_at_eof(self, lines: List[str], line_num: int) -> Tuple[bool, str, str]:
        """🔧 Fix W292: no newline at end of file"""
        if not lines:
            return False, "", "Empty file"

        last_line = lines[-1]
        if not last_line.endswith('\n'):
            lines[-1] = last_line + '\n'
            return True, last_line, last_line + '\\n'

        return False, last_line, "Already has newline"

    def _fix_e301_expected_blank_line(
        self, lines: List[str], line_num: int) -> Tuple[bool, str, str]:
        """🔧 Fix E301: expected 1 blank line"""
        if line_num <= 1:
            return False, "", "At file start"

        original_line = lines[line_num - 1]

        # Add blank line before current line
        lines.insert(line_num - 1, '\n')
        return True, original_line.rstrip(), "Added blank line"

    def _fix_e261_inline_comment_spacing(
        self, lines: List[str], line_num: int) -> Tuple[bool, str, str]:
        """🔧 Fix E261: inline comment should start with '#'"""
        if line_num <= 0 or line_num > len(lines):
            return False, "", "Invalid line number"

        original_line = lines[line_num - 1]

        # Fix inline comment spacing
        if '#' in original_line and not original_line.strip().startswith('#'):
            # Find comment position
            comment_pos = original_line.find('#')
            before_comment = original_line[:comment_pos]
            comment_part = original_line[comment_pos:]

            # Ensure proper spacing before #
            if comment_pos > 0 and original_line[comment_pos - 1] != ' ':
                fixed_line = before_comment + ' ' + comment_part
                lines[line_num - 1] = fixed_line
                return True, original_line.rstrip(), fixed_line.rstrip()

        return False, original_line, "No inline comment issue"

    def fix_violations_in_file(self, file_path: str, violations: List[Tuple]) -> List[FixResult]:
        """🔧 Fix all violations in a specific file"""
        results = []

        # Create backup
        backup_path = self.create_file_backup(file_path)
        if not backup_path:
            print(f"⚠️  Could not backup {file_path}")
            return results

        # Read file
        try:
            lines = self.read_file_lines(file_path)
        except Exception as e:
            print(f"❌ Error reading {file_path}: {e}")
            return results

        # Sort violations by line number (descending to avoid line number shifts)
        violations_sorted = sorted(violations, key=lambda v: v[2], reverse=True)

        file_modified = False

        for violation in violations_sorted:
            violation_id, _, line_number, column_number, error_code, message = violation

            if error_code in self.fixers:
                try:
                    success, original, fixed = self.fixers[error_code](lines, line_number)

                    result = FixResult(
                        violation_id=violation_id,
                        file_path=file_path,
                        line_number=line_number,
                        error_code=error_code,
                        original_line=original,
                        fixed_line=fixed,
                        success=success
                    )

                    if success:
                        file_modified = True

                    results.append(result)

                except Exception as e:
                    result = FixResult(
                        violation_id=violation_id,
                        file_path=file_path,
                        line_number=line_number,
                        error_code=error_code,
                        original_line="",
                        fixed_line="",
                        success=False,
                        error_message=str(e)
                    )
                    results.append(result)

        # Write file if modified
        if file_modified:
            if self.write_file_lines(file_path, lines):
                print(
                    f"✅ Fixed {sum(1 for r in results if r.success)} violations in {Path(file_path).name}")
            else:
                print(f"❌ Error writing {file_path}")
                # Restore from backup
                shutil.copy2(backup_path, file_path)

        return results

    def update_database_corrections(self, results: List[FixResult]):
        """💾 Update database with correction results"""
        with sqlite3.connect(self.database_path) as conn:
            cursor = conn.cursor()

            for result in results:
                if result.success:
                    # Mark violation as fixed
                    cursor.execute("""
                        UPDATE violations 
                        SET status = 'fixed' 
                        WHERE id = ?
                    """, (result.violation_id,))

                    # Record correction
                    cursor.execute("""
                        INSERT INTO corrections 
                        (violation_id, correction_applied, success, timestamp)
                        VALUES (?, ?, ?, ?)
                    """, (
                        result.violation_id,
                        f"{result.error_code}: {result.original_line} -> {result.fixed_line}",
                        True,
                        datetime.now()
                    ))

    def fix_all_violations(self, max_files: int = 10) -> Dict[str, Any]:
        """🔧 Fix violations across multiple files"""
        start_time = datetime.now()
        print("🚀 STARTING AUTOMATED VIOLATION FIXES")

        # Get fixable violations
        violations = self.get_fixable_violations()
        print(f"📊 Found {len(violations)} fixable violations")

        # Group by file
        files_violations = {}
        for violation in violations:
            file_path = violation[1]
            if file_path not in files_violations:
                files_violations[file_path] = []
            files_violations[file_path].append(violation)

        print(f"📁 {len(files_violations)} files need fixes")

        # Limit files processed
        files_to_process = list(files_violations.keys())[:max_files]

        all_results = []
        total_fixed = 0

        with tqdm(total=len(files_to_process), desc="🔧 Fixing Files", unit="files") as pbar:
            for file_path in files_to_process:
                pbar.set_description(f"🔧 {Path(file_path).name}")

                file_violations = files_violations[file_path]
                results = self.fix_violations_in_file(file_path, file_violations)

                fixed_count = sum(1 for r in results if r.success)
                total_fixed += fixed_count

                all_results.extend(results)
                pbar.update(1)

        # Update database
        print("💾 Updating database...")
        self.update_database_corrections(all_results)

        duration = (datetime.now() - start_time).total_seconds()

        return {
            "files_processed": len(files_to_process),
            "total_violations_attempted": len(violations),
            "total_violations_fixed": total_fixed,
            "success_rate": (total_fixed / len(violations)) * 100 if violations else 0,
            "duration_seconds": duration,
            "results": all_results
        }


def main():
    """🔧 Main execution function with enterprise monitoring"""
    # MANDATORY: Start time and process tracking
    start_time = datetime.now()
    process_id = os.getpid()

    print("=" * 80)
    print("🔧 AUTOMATED VIOLATIONS FIXER")
    print("=" * 80)
    print(f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Process ID: {process_id}")
    print("Target: 12,844+ violations automated fixes")
    print()

    try:
        # Initialize fixer
        fixer = AutomatedViolationsFixer()

        # Fix violations (start with 10 files)
        print("🔧 Starting automated fixes...")
        results = fixer.fix_all_violations(max_files=10)

        # Success summary
        duration = (datetime.now() - start_time).total_seconds()
        print("\n" + "=" * 80)
        print("✅ AUTOMATED FIXES COMPLETED")
        print("=" * 80)
        print(f"📁 Files Processed: {results['files_processed']}")
        print(f"🔧 Violations Attempted: {results['total_violations_attempted']:,}")
        print(f"✅ Violations Fixed: {results['total_violations_fixed']:,}")
        print(f"📊 Success Rate: {results['success_rate']:.1f}%")
        print(f"⏱️  Duration: {duration:.2f} seconds")
        print(f"💾 Backup Location: {fixer.backup_dir}")
        print("=" * 80)

        # Show fix breakdown
        if results['results']:
            print("\n🎯 FIX BREAKDOWN BY TYPE:")
            fix_counts = {}
            for result in results['results']:
                if result.success:
                    if result.error_code not in fix_counts:
                        fix_counts[result.error_code] = 0
                    fix_counts[result.error_code] += 1

            for error_code, count in sorted(fix_counts.items()):
                print(f"   {error_code}: {count:,} fixes")

    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds()
        print(f"\n❌ ERROR: {e}")
        print(f"⏱️  Duration: {duration:.2f} seconds")
        sys.exit(1)

if __name__ == "__main__":
    main()
