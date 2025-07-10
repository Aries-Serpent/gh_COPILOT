#!/usr/bin/env python3
"""
ENHANCED SYSTEMATIC FLAKE8 CORRECTOR SYSTEM
==================================================
Enhanced systematic corrector implementing comprehensive error analysis and
advanced correction patterns based on proven methodologies.

Features:
- Advanced pattern recognition and correction
- Comprehensive backup and validation
- Smart file filtering (excludes backups, .git, etc.)
- Database-driven learning and pattern storage
- Multi-threaded processing for efficiency
- Detailed logging and reporting
"""

import os
import sys
import json
import sqlite3
import shutil
import subprocess
import re
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, asdict
import ast
from concurrent.futures import ThreadPoolExecutor, as_completed


@dataclass
class ErrorPattern:
    """Enhanced error pattern for systematic corrections"""
    error_code: str
    pattern_name: str
    pattern_regex: str
    correction_template: str
    priority: int
    success_rate: float = 0.0
    usage_count: int = 0


@dataclass
class FileCorrection:
    """Enhanced file correction result"""
    file_path: str
    original_errors: int
    fixed_errors: int
    backup_created: bool
    validation_passed: bool
    patterns_applied: List[str]
    correction_time: float
    notes: str


class EnhancedSystematicFlake8Corrector:
    """Enhanced systematic Flake8 corrector with advanced patterns"""

    def __init__(self, workspace_root: str):
        self.workspace_root = Path(workspace_root)
        self.db_path = self.workspace_root / "databases" / "analytics.db"
        self.backup_dir = self.workspace_root / "backups" / f"enhanced_corrections_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.log_dir = self.workspace_root / "logs"

        # Ensure directories exist
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Setup logging
        self._setup_logging()

        # Initialize database
        self._init_database()

        # Load enhanced correction patterns
        self.patterns = self._load_enhanced_patterns()

        # File exclusion patterns
        self.exclude_patterns = {
            "backups/", ".git/", "__pycache__/", ".pytest_cache/",
            "node_modules/", ".venv/", "venv/", ".mypy_cache/"
        }

    def _setup_logging(self):
        """Setup enhanced logging"""
        log_file = self.log_dir / f"enhanced_systematic_corrections_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def _init_database(self):
        """Initialize enhanced analytics database"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS error_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    error_code TEXT NOT NULL,
                    pattern_name TEXT NOT NULL,
                    pattern_regex TEXT NOT NULL,
                    correction_template TEXT NOT NULL,
                    priority INTEGER NOT NULL,
                    success_rate REAL DEFAULT 0.0,
                    usage_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS correction_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    original_errors INTEGER NOT NULL,
                    fixed_errors INTEGER NOT NULL,
                    patterns_applied TEXT NOT NULL,
                    validation_passed BOOLEAN NOT NULL,
                    correction_time REAL NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def _load_enhanced_patterns(self) -> List[ErrorPattern]:
        """Load enhanced correction patterns with proven success rates"""
        enhanced_patterns = [
            # Critical E999 Syntax Errors - High Priority
            ErrorPattern(
                error_code="E999",
                pattern_name="mismatched_brackets_parentheses",
                pattern_regex=r"closing parenthesis '(\]|\))' does not match opening parenthesis '(\(|\[)'",
                correction_template="bracket_mismatch_fix",
                priority=1
            ),
            ErrorPattern(
                error_code="E999",
                pattern_name="indentation_error_unexpected",
                pattern_regex=r"IndentationError: unexpected indent",
                correction_template="indentation_fix",
                priority=1
            ),
            ErrorPattern(
                error_code="E999",
                pattern_name="unmatched_brackets",
                pattern_regex=r"unmatched '(\]|\)|\})'",
                correction_template="unmatched_bracket_fix",
                priority=1
            ),
            ErrorPattern(
                error_code="E999",
                pattern_name="unterminated_string",
                pattern_regex=r"unterminated string literal",
                correction_template="string_termination_fix",
                priority=1
            ),
            ErrorPattern(
                error_code="E999",
                pattern_name="invalid_syntax",
                pattern_regex=r"invalid syntax",
                correction_template="syntax_repair",
                priority=1
            ),

            # Style and Format Errors - Medium Priority
            ErrorPattern(
                error_code="E501",
                pattern_name="line_too_long",
                pattern_regex=r"line too long \((\d+) > 79 characters\)",
                correction_template="line_length_fix",
                priority=3
            ),
            ErrorPattern(
                error_code="E302",
                pattern_name="missing_blank_lines",
                pattern_regex=r"expected 2 blank lines, found (\d+)",
                correction_template="blank_lines_fix",
                priority=3
            ),
            ErrorPattern(
                error_code="W291",
                pattern_name="trailing_whitespace",
                pattern_regex=r"trailing whitespace",
                correction_template="whitespace_cleanup",
                priority=4
            ),
            ErrorPattern(
                error_code="W293",
                pattern_name="blank_line_whitespace",
                pattern_regex=r"blank line contains whitespace",
                correction_template="blank_line_cleanup",
                priority=4
            ),

            # Import and Logic Errors - High Priority
            ErrorPattern(
                error_code="F401",
                pattern_name="unused_import",
                pattern_regex=r"'([^']+)' imported but unused",
                correction_template="remove_unused_import",
                priority=2
            ),
            ErrorPattern(
                error_code="F821",
                pattern_name="undefined_name",
                pattern_regex=r"undefined name '([^']+)'",
                correction_template="define_missing_name",
                priority=2
            ),
            ErrorPattern(
                error_code="F541",
                pattern_name="f_string_missing_placeholder",
                pattern_regex=r"f-string is missing placeholders",
                correction_template="fix_f_string",
                priority=3
            )
        ]

        # Store patterns in database
        self._store_patterns_in_db(enhanced_patterns)
        return enhanced_patterns

    def _store_patterns_in_db(self, patterns: List[ErrorPattern]):
        """Store patterns in database for learning and tracking"""
        with sqlite3.connect(self.db_path) as conn:
            for pattern in patterns:
                conn.execute("""
                    INSERT OR REPLACE INTO error_patterns
                    (error_code, pattern_name, pattern_regex, correction_template, priority)
                    VALUES (?, ?, ?, ?, ?)
                """, (pattern.error_code, pattern.pattern_name, pattern.pattern_regex,
                     pattern.correction_template, pattern.priority))

    def should_exclude_file(self, file_path: str) -> bool:
        """Enhanced file exclusion logic"""
        file_path_str = str(file_path).replace('\\', '/')

        # Skip if in excluded directories
        for pattern in self.exclude_patterns:
            if pattern in file_path_str:
                return True

        # Skip non-Python files
        if not file_path_str.endswith('.py'):
            return True

        return False

    def run_flake8_scan(self) -> str:
        """Run comprehensive Flake8 scan with enhanced filtering"""
        self.logger.info("Running enhanced Flake8 scan...")

        output_file = self.workspace_root / f"flake8_enhanced_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

        # Enhanced Flake8 command with better exclusions
        cmd = [
            "python", "-m", "flake8",
            "--statistics", "--count",
            "--extend-ignore=E203,W503",
            "--max-line-length=79",
            f"--exclude=backups,.git,__pycache__,.pytest_cache,node_modules,.venv,venv,.mypy_cache",
            "."
        ]

        try:
            result = subprocess.run(
                cmd,
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            output = result.stdout + result.stderr

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(output)

            self.logger.info(f"Flake8 scan completed. Output saved to: {output_file}")
            return output

        except subprocess.TimeoutExpired:
            self.logger.error("Flake8 scan timed out")
            return ""
        except Exception as e:
            self.logger.error(f"Error running Flake8: {e}")
            return ""

    def parse_flake8_output(self, flake8_output: str) -> List[Dict]:
        """Enhanced Flake8 output parsing with better error extraction"""
        errors = []

        for line in flake8_output.split('\n'):
            line = line.strip()
            if not line or line.startswith('.\\') == False:
                continue

            # Enhanced regex for Flake8 error parsing
            match = re.match(r'(.+):(\d+):(\d+):\s+([A-Z]\d+)\s+(.+)', line)
            if match:
                file_path, line_num, col_num, error_code, message = match.groups()

                # Skip if file should be excluded
                if self.should_exclude_file(file_path):
                    continue

                errors.append({
                    'file_path': file_path,
                    'line_number': int(line_num),
                    'column_number': int(col_num),
                    'error_code': error_code,
                    'message': message,
                    'full_line': line
                })

        self.logger.info(f"Parsed {len(errors)} errors from Flake8 output")
        return errors

    def categorize_errors_by_severity(self, errors: List[Dict]) -> Dict[str, List[Dict]]:
        """Enhanced error categorization with better severity mapping"""
        categorized = {
            'critical': [],
            'high': [],
            'medium': [],
            'low': []
        }

        severity_mapping = {
            'E999': 'critical',  # Syntax errors
            'E901': 'critical',  # IndentationError
            'E902': 'critical',  # IOError
            'F821': 'high',      # Undefined name
            'F822': 'high',      # Undefined name in __all__
            'F823': 'high',      # Local variable referenced before assignment
            'E501': 'medium',    # Line too long
            'E302': 'medium',    # Expected 2 blank lines
            'E305': 'medium',    # Expected 2 blank lines after class/function
            'F401': 'medium',    # Imported but unused
            'F841': 'medium',    # Local variable assigned but never used
            'W291': 'low',       # Trailing whitespace
            'W293': 'low',       # Blank line contains whitespace
            'F541': 'low',       # f-string missing placeholders
        }

        for error in errors:
            error_code = error['error_code']
            severity = severity_mapping.get(error_code, 'low')
            categorized[severity].append(error)

        return categorized

    def apply_correction_pattern(self, file_path: str, error: Dict, pattern: ErrorPattern) -> bool:
        """Enhanced pattern application with better success tracking"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            original_content = content
            fixed = False

            # Apply specific correction based on pattern
            if pattern.correction_template == "bracket_mismatch_fix":
                content, fixed = self._fix_bracket_mismatch(content, error)
            elif pattern.correction_template == "indentation_fix":
                content, fixed = self._fix_indentation_error(content, error)
            elif pattern.correction_template == "line_length_fix":
                content, fixed = self._fix_line_length(content, error)
            elif pattern.correction_template == "remove_unused_import":
                content, fixed = self._remove_unused_import(content, error)
            elif pattern.correction_template == "whitespace_cleanup":
                content, fixed = self._cleanup_whitespace(content, error)
            elif pattern.correction_template == "blank_line_cleanup":
                content, fixed = self._cleanup_blank_lines(content, error)
            elif pattern.correction_template == "fix_f_string":
                content, fixed = self._fix_f_string(content, error)

            if fixed and content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)

                # Update pattern success rate
                self._update_pattern_success(pattern.pattern_name, True)
                return True

        except Exception as e:
            self.logger.error(f"Error applying pattern {pattern.pattern_name} to {file_path}: {e}")
            self._update_pattern_success(pattern.pattern_name, False)

        return False

    def _fix_bracket_mismatch(self, content: str, error: Dict) -> Tuple[str, bool]:
        """Fix bracket/parenthesis mismatches"""
        lines = content.split('\n')
        line_idx = error['line_number'] - 1

        if line_idx < len(lines):
            line = lines[line_idx]

            # Common bracket mismatch fixes
            if ']' in line and '(' in line and ')' not in line:
                # Replace ] with ) if there's an opening (
                fixed_line = line.replace(']', ')', 1)
                lines[line_idx] = fixed_line
                return '\n'.join(lines), True
            elif ')' in line and '[' in line and ']' not in line:
                # Replace ) with ] if there's an opening [
                fixed_line = line.replace(')', ']', 1)
                lines[line_idx] = fixed_line
                return '\n'.join(lines), True

        return content, False

    def _fix_indentation_error(self, content: str, error: Dict) -> Tuple[str, bool]:
        """Fix indentation errors"""
        lines = content.split('\n')
        line_idx = error['line_number'] - 1

        if line_idx < len(lines):
            line = lines[line_idx]

            # Remove unexpected indentation
            if line.strip() and line.startswith('    ') or line.startswith('\t'):
                # Check if this is really unexpected by looking at previous line
                if line_idx > 0:
                    prev_line = lines[line_idx - 1].strip()
                    if not prev_line.endswith(':') and not prev_line.endswith('\\'):
                        # Remove indentation
                        lines[line_idx] = line.lstrip()
                        return '\n'.join(lines), True

        return content, False

    def _fix_line_length(self, content: str, error: Dict) -> Tuple[str, bool]:
        """Fix line length issues"""
        lines = content.split('\n')
        line_idx = error['line_number'] - 1

        if line_idx < len(lines):
            line = lines[line_idx]

            if len(line) > 79:
                # Try to break at logical points
                if ', ' in line and len(line) > 79:
                    # Break at comma
                    parts = line.split(', ')
                    if len(parts) > 1:
                        # Find a good break point
                        new_lines = []
                        current_line = parts[0]

                        for part in parts[1:]:
                            test_line = current_line + ', ' + part
                            if len(test_line) <= 79:
                                current_line = test_line
                            else:
                                new_lines.append(current_line + ',')
                                current_line = '    ' + part  # Indent continuation

                        new_lines.append(current_line)

                        # Replace the long line with broken lines
                        lines[line_idx:line_idx+1] = new_lines
                        return '\n'.join(lines), True

        return content, False

    def _remove_unused_import(self, content: str, error: Dict) -> Tuple[str, bool]:
        """Remove unused imports"""
        lines = content.split('\n')
        line_idx = error['line_number'] - 1

        if line_idx < len(lines):
            line = lines[line_idx]

            # Extract import name from error message
            match = re.search(r"'([^']+)' imported but unused", error['message'])
            if match:
                import_name = match.group(1)

                # Remove the import line if it only contains this import
                if f"import {import_name}" in line and line.strip().startswith('import'):
                    lines.pop(line_idx)
                    return '\n'.join(lines), True
                elif f"from {import_name}" in line and line.strip().startswith('from'):
                    lines.pop(line_idx)
                    return '\n'.join(lines), True

        return content, False

    def _cleanup_whitespace(self, content: str, error: Dict) -> Tuple[str, bool]:
        """Remove trailing whitespace"""
        lines = content.split('\n')
        line_idx = error['line_number'] - 1

        if line_idx < len(lines):
            line = lines[line_idx]
            if line.rstrip() != line:
                lines[line_idx] = line.rstrip()
                return '\n'.join(lines), True

        return content, False

    def _cleanup_blank_lines(self, content: str, error: Dict) -> Tuple[str, bool]:
        """Clean up blank lines with whitespace"""
        lines = content.split('\n')
        line_idx = error['line_number'] - 1

        if line_idx < len(lines):
            line = lines[line_idx]
            if line.strip() == '' and line != '':
                lines[line_idx] = ''
                return '\n'.join(lines), True

        return content, False

    def _fix_f_string(self, content: str, error: Dict) -> Tuple[str, bool]:
        """Fix f-strings missing placeholders"""
        lines = content.split('\n')
        line_idx = error['line_number'] - 1

        if line_idx < len(lines):
            line = lines[line_idx]

            # Convert f-string to regular string if no placeholders
            if line.count('f"') > 0 and '{' not in line:
                fixed_line = line.replace('f"', '"')
                lines[line_idx] = fixed_line
                return '\n'.join(lines), True
            elif line.count("f'") > 0 and '{' not in line:
                fixed_line = line.replace("f'", "'")
                lines[line_idx] = fixed_line
                return '\n'.join(lines), True

        return content, False

    def _update_pattern_success(self, pattern_name: str, success: bool):
        """Update pattern success rate in database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE error_patterns
                SET usage_count = usage_count + 1,
                    success_rate = CASE
                        WHEN usage_count = 0 THEN ?
                        ELSE (success_rate * usage_count + ?) / (usage_count + 1)
                    END,
                    updated_at = CURRENT_TIMESTAMP
                WHERE pattern_name = ?
            """, (1.0 if success else 0.0, 1.0 if success else 0.0, pattern_name))

    def correct_file(self, file_path: str, errors: List[Dict]) -> FileCorrection:
        """Enhanced file correction with comprehensive pattern application"""
        start_time = datetime.now()

        # Create backup
        backup_path = self.backup_dir / Path(file_path).name
        shutil.copy2(file_path, backup_path)

        original_error_count = len(errors)
        fixed_errors = 0
        patterns_applied = []

        # Sort patterns by priority
        sorted_patterns = sorted(self.patterns, key=lambda p: p.priority)

        # Apply corrections for each error
        for error in errors:
            for pattern in sorted_patterns:
                if pattern.error_code == error['error_code']:
                    if self.apply_correction_pattern(file_path, error, pattern):
                        fixed_errors += 1
                        patterns_applied.append(pattern.pattern_name)
                        break

        # Validate corrections
        validation_passed = self._validate_syntax(file_path)

        correction_time = (datetime.now() - start_time).total_seconds()

        return FileCorrection(
            file_path=file_path,
            original_errors=original_error_count,
            fixed_errors=fixed_errors,
            backup_created=True,
            validation_passed=validation_passed,
            patterns_applied=patterns_applied,
            correction_time=correction_time,
            notes=f"Applied {len(set(patterns_applied))} unique patterns"
        )

    def _validate_syntax(self, file_path: str) -> bool:
        """Validate Python syntax after corrections"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            ast.parse(content)
            return True
        except SyntaxError:
            return False
        except Exception:
            return False

    def process_critical_errors(self, max_files: int = 50) -> Dict:
        """Process critical errors with enhanced systematic approach"""
        self.logger.info("Starting enhanced critical error processing...")

        session_id = f"ENHANCED_CRITICAL_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Run Flake8 scan
        flake8_output = self.run_flake8_scan()

        # Parse and categorize errors
        all_errors = self.parse_flake8_output(flake8_output)
        categorized_errors = self.categorize_errors_by_severity(all_errors)

        critical_errors = categorized_errors['critical']

        self.logger.info(f"Found {len(critical_errors)} critical errors")

        # Group errors by file
        errors_by_file = {}
        for error in critical_errors:
            file_path = error['file_path']
            if file_path not in errors_by_file:
                errors_by_file[file_path] = []
            errors_by_file[file_path].append(error)

        # Process files (limit to max_files)
        files_to_process = list(errors_by_file.keys())[:max_files]
        results = []

        self.logger.info(f"Processing {len(files_to_process)} files...")

        # Use threading for efficiency
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {}

            for file_path in files_to_process:
                if not self.should_exclude_file(file_path):
                    file_errors = errors_by_file[file_path]
                    future = executor.submit(self.correct_file, file_path, file_errors)
                    futures[future] = file_path

            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                    self.logger.info(f"Processed {result.file_path}: {result.fixed_errors}/{result.original_errors} errors fixed")
                except Exception as e:
                    file_path = futures[future]
                    self.logger.error(f"Error processing {file_path}: {e}")

        # Save results to database
        self._save_correction_results(session_id, results)

        # Generate summary report
        summary = {
            'session_id': session_id,
            'total_files_processed': len(results),
            'total_errors_found': sum(r.original_errors for r in results),
            'total_errors_fixed': sum(r.fixed_errors for r in results),
            'validation_success_rate': sum(1 for r in results if r.validation_passed) / len(results) if results else 0,
            'average_correction_time': sum(r.correction_time for r in results) / len(results) if results else 0,
            'unique_patterns_used': len(set(pattern for r in results for pattern in r.patterns_applied)),
            'results': [asdict(r) for r in results]
        }

        # Save summary report
        report_file = self.workspace_root / f"enhanced_correction_report_{session_id}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)

        self.logger.info(f"Enhanced correction completed. Report saved to: {report_file}")
        return summary

    def _save_correction_results(self, session_id: str, results: List[FileCorrection]):
        """Save correction results to database"""
        with sqlite3.connect(self.db_path) as conn:
            for result in results:
                conn.execute("""
                    INSERT INTO correction_results
                    (session_id, file_path, original_errors, fixed_errors, patterns_applied,
                     validation_passed, correction_time)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (session_id, result.file_path, result.original_errors, result.fixed_errors,
                     json.dumps(result.patterns_applied), result.validation_passed, result.correction_time))


def main():
    """Main execution function"""
    print("ENHANCED SYSTEMATIC FLAKE8 CORRECTOR SYSTEM")
    print("=" * 60)
    print("Advanced systematic error correction with enhanced patterns...")
    print("=" * 60)

    workspace = os.environ.get('WORKSPACE_ROOT', os.getcwd())

    corrector = EnhancedSystematicFlake8Corrector(workspace)

    try:
        # Process critical errors first
        summary = corrector.process_critical_errors(max_files=30)

        print(f"\nENHANCED CORRECTION SUMMARY")
        print("=" * 60)
        print(f"Session ID: {summary['session_id']}")
        print(f"Files Processed: {summary['total_files_processed']}")
        print(f"Total Errors Found: {summary['total_errors_found']}")
        print(f"Total Errors Fixed: {summary['total_errors_fixed']}")
        print(f"Validation Success Rate: {summary['validation_success_rate']:.2%}")
        print(f"Average Correction Time: {summary['average_correction_time']:.2f}s")
        print(f"Unique Patterns Used: {summary['unique_patterns_used']}")
        print("=" * 60)
        print("ENHANCED SYSTEMATIC CORRECTION COMPLETE!")

    except Exception as e:
        corrector.logger.error(f"Critical error in enhanced corrector: {e}")
        raise


if __name__ == "__main__":
    main()
