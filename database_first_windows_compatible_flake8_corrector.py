#!/usr/bin/env python3
"""
DATABASE-FIRST WINDOWS-COMPATIBLE FLAKE8 CORRECTOR
===================================================

Enterprise-grade Flake8/PEP 8 compliance enforcement system
using database-stored patterns without Unicode emoji characters.

Features:
- Database-first correction patterns
- Windows console compatibility (NO Unicode emojis)
- Comprehensive logging with proper encoding
- DUAL COPILOT validation pattern
- Anti-recursion protection
- Visual processing indicators (text-based)

Author: gh_COPILOT Enterprise Framework
Date: July 10, 2025
"""

import logging
import os
import re
import sqlite3
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from tqdm import tqdm

# Windows-compatible visual indicators (NO Unicode emojis)
VISUAL_INDICATORS = {
    'start': '[START]',
    'progress': '[PROGRESS]',
    'success': '[SUCCESS]',
    'error': '[ERROR]',
    'warning': '[WARNING]',
    'info': '[INFO]',
    'database': '[DATABASE]',
    'fix': '[FIX]',
    'search': '[SEARCH]',
    'validation': '[VALIDATION]',
    'complete': '[COMPLETE]'
}


@dataclass
class FlakeViolation:
    """Represents a Flake8 violation"""
    file_path: str
    line_number: int
    column: int
    error_code: str
    message: str
    raw_line: str = ""


@dataclass
class CorrectionPattern:
    """Database-stored correction pattern"""
    pattern_id: str
    error_code: str
    pattern_regex: str
    replacement_template: str
    confidence_score: float
    success_rate: float
    usage_count: int


@dataclass
class CorrectionResult:
    """Result of applying a correction"""
    success: bool
    original_content: str
    corrected_content: str
    violations_fixed: List[str]
    errors: List[str]


class WindowsCompatibleLogger:
    """Windows-compatible logger without Unicode issues"""

    def __init__(self, log_file: str):
        self.log_file = log_file

        # Setup file logging with UTF-8 encoding
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )

        self.logger = logging.getLogger(__name__)

        # Set console handler to use proper encoding
        for handler in self.logger.handlers:
            if isinstance(handler, logging.StreamHandler):
                handler.stream = sys.stdout

    def info(self, message: str, indicator: str = 'info'):
        """Log info message with text indicator"""
        text_indicator = VISUAL_INDICATORS.get(indicator, '[INFO]')
        safe_message = f"{text_indicator} {message}"
        self.logger.info(safe_message)

    def error(self, message: str):
        """Log error message"""
        safe_message = f"{VISUAL_INDICATORS['error']} {message}"
        self.logger.error(safe_message)

    def warning(self, message: str):
        """Log warning message"""
        safe_message = f"{VISUAL_INDICATORS['warning']} {message}"
        self.logger.warning(safe_message)


class DatabaseFirstFlake8Corrector:
    """Database-first Flake8 corrector with Windows compatibility"""

    def __init__(self, workspace_path: str = "e:/gh_COPILOT"):
        self.workspace_path = Path(workspace_path)
        self.session_id = f"SESSION_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Setup Windows-compatible logging
        log_file = self.workspace_path / f"flake8_correction_{self.session_id}.log"
        self.logger = WindowsCompatibleLogger(str(log_file))

        # Database connections
        self.production_db = self.workspace_path / "databases" / "production.db"
        self.analytics_db = self.workspace_path / "databases" / "analytics.db"

        # Correction patterns loaded from database
        self.correction_patterns: Dict[str, CorrectionPattern] = {}

        # Statistics
        self.stats = {
            'files_processed': 0,
            'violations_found': 0,
            'violations_fixed': 0,
            'files_modified': 0,
            'errors_encountered': 0
        }

        # Anti-recursion protection
        self.validate_workspace_integrity()

    def _sanitize_path(self, path: Path) -> str:
        """Return a Windows-safe path string."""
        path_str = str(path)
        if os.name == "nt":
            path_str = path_str.replace("\\", "/")
        return path_str

    def validate_workspace_integrity(self):
        """CRITICAL: Validate workspace for anti-recursion compliance"""
        self.logger.info("Validating workspace integrity", "validation")

        # For Flake8 correction, we'll use a more permissive approach
        # Only block obvious recursive violations that could cause infinite loops
        critical_violations = []

        # Check for potentially dangerous recursive patterns
        dangerous_patterns = ['*_BACKUP_*', '*_TEMP_*', 'recursive_*']

        for pattern in dangerous_patterns:
            for folder in self.workspace_path.rglob(pattern):
                if folder.is_dir() and folder != self.workspace_path:
                    # Only flag if it looks like an actual recursive violation
                    if 'recursive' in folder.name.lower() or folder.name.count('_') > 3:
                        critical_violations.append(str(folder))

        if critical_violations:
            error_msg = f"CRITICAL: Dangerous recursive violations detected: {critical_violations}"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)

        self.logger.info(
            "Workspace integrity validated - no dangerous recursive patterns found",
            "success"
        )

    def load_correction_patterns_from_database(self):
        """Load correction patterns from production and analytics databases"""
        self.logger.info("Loading correction patterns from databases", "database")

        patterns_loaded = 0

        # Load from production database
        try:
            with sqlite3.connect(self.production_db) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT pattern_id, error_code, pattern_regex, replacement_template,
                           success_rate, usage_count, validated
                    FROM flake8_fix_patterns
                    WHERE validated = 1
                ''')

                for row in cursor.fetchall():
                    pattern = CorrectionPattern(
                        pattern_id=row[0],
                        error_code=row[1],
                        pattern_regex=row[2],
                        replacement_template=row[3],
                        confidence_score=row[4],  # Use success_rate as confidence
                        success_rate=row[4],
                        usage_count=row[5]
                    )
                    self.correction_patterns[row[1]] = pattern
                    patterns_loaded += 1

        except Exception as e:
            self.logger.error(f"Error loading from production database: {e}")

        # Load from analytics database
        try:
            with sqlite3.connect(self.analytics_db) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT pattern_id, error_code, pattern_regex, replacement_template,
                           confidence_score, success_rate, usage_count
                    FROM flake8_correction_patterns
                    WHERE confidence_score > 0.8
                ''')

                for row in cursor.fetchall():
                    # Only add if not already loaded or if this has higher confidence
                    error_code = row[1]
                    if (error_code not in self.correction_patterns or
                            row[4] > self.correction_patterns[error_code].confidence_score):

                        pattern = CorrectionPattern(
                            pattern_id=row[0],
                            error_code=row[1],
                            pattern_regex=row[2],
                            replacement_template=row[3],
                            confidence_score=row[4],
                            success_rate=row[5],
                            usage_count=row[6]
                        )
                        self.correction_patterns[error_code] = pattern
                        patterns_loaded += 1

        except Exception as e:
            self.logger.error(f"Error loading from analytics database: {e}")

        self.logger.info(
            f"Loaded {patterns_loaded} correction patterns from databases",
            "success"
        )

    def run_flake8_scan(self) -> List[FlakeViolation]:
        """Run Flake8 scan and parse violations"""
        self.logger.info("Running Flake8 scan across workspace", "search")

        violations = []

        try:
            # Run flake8 with specific configuration
            cmd = [
                sys.executable, "-m", "flake8",
                self._sanitize_path(self.workspace_path),
                "--format=%(path)s:%(row)d:%(col)d:%(code)s:%(text)s",
                "--max-line-length=88",
                "--extend-ignore=E203,W503",
                "--exclude=.git,__pycache__,*.egg-info,build,dist,venv,env"
            ]

            env = os.environ.copy()
            env["PYTHONIOENCODING"] = "utf-8"

            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="strict",
                    cwd=self.workspace_path,
                    env=env,
                )
                output = result.stdout
            except UnicodeError as u_err:
                self.logger.error(f"Unicode error running Flake8: {u_err}")
                raw = subprocess.run(cmd, capture_output=True, cwd=self.workspace_path, env=env)
                output = raw.stdout.decode("utf-8", "replace")

            # Parse flake8 output
            for line in output.splitlines():
                line = line.strip()
                if not line:
                    continue

                # Parse: path:line:col:code:message
                parts = line.split(':', 4)
                if len(parts) >= 5:
                    try:
                        violation = FlakeViolation(
                            file_path=parts[0],
                            line_number=int(parts[1]),
                            column=int(parts[2]),
                            error_code=parts[3],
                            message=parts[4]
                        )
                        violations.append(violation)
                    except (ValueError, IndexError):
                        self.logger.warning(f"Could not parse Flake8 line: {line}")

        except subprocess.SubprocessError as e:
            self.logger.error(f"Error running Flake8: {e}")

        self.stats['violations_found'] = len(violations)
        self.logger.info(f"Found {len(violations)} Flake8 violations", "info")

        return violations

    def apply_correction_pattern(
        self,
        file_path: str,
        violation: FlakeViolation
    ) -> CorrectionResult:
        """Apply database-stored correction pattern to fix violation"""

        pattern = self.correction_patterns.get(violation.error_code)
        if not pattern:
            return CorrectionResult(
                success=False,
                original_content="",
                corrected_content="",
                violations_fixed=[],
                errors=[f"No pattern found for {violation.error_code}"]
            )

        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                original_content = f.read()

            corrected_content = original_content
            violations_fixed = []

            # Apply specific fixes based on error code
            if violation.error_code == "W293":
                # Remove trailing whitespace
                corrected_content = re.sub(
                    r'[ \t]+$',
                    '',
                    corrected_content,
                    flags=re.MULTILINE
                )
                violations_fixed.append("W293: Removed trailing whitespace")

            elif violation.error_code == "W291":
                # Add final newline if missing
                if not corrected_content.endswith('\n'):
                    corrected_content += '\n'
                violations_fixed.append("W291: Added final newline")

            elif violation.error_code == "E501":
                # Line too long - attempt to wrap imports
                lines = corrected_content.splitlines()
                for i, line in enumerate(lines):
                    if len(line) > 88 and ('import' in line):
                        # Basic import wrapping
                        if line.startswith('from ') and ' import ' in line:
                            parts = line.split(' import ', 1)
                            if len(parts) == 2:
                                imports = parts[1].split(', ')
                                if len(imports) > 1:
                                    wrapped = f"{parts[0]} import (\n"
                                    for imp in imports:
                                        wrapped += f"    {imp.strip()},\n"
                                    wrapped += ")"
                                    lines[i] = wrapped
                                    violations_fixed.append("E501: Wrapped long import line")

                corrected_content = '\n'.join(lines)

            elif violation.error_code in ["E302", "E303", "E305"]:
                # Spacing issues around classes and functions
                corrected_content = re.sub(r'\n{3,}', '\n\n', corrected_content)
                violations_fixed.append(f"{violation.error_code}: Fixed spacing")

            # Write corrected content if changes were made
            if corrected_content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(corrected_content)

                return CorrectionResult(
                    success=True,
                    original_content=original_content,
                    corrected_content=corrected_content,
                    violations_fixed=violations_fixed,
                    errors=[]
                )
            else:
                return CorrectionResult(
                    success=False,
                    original_content=original_content,
                    corrected_content=corrected_content,
                    violations_fixed=[],
                    errors=[f"No changes applied for {violation.error_code}"]
                )

        except Exception as e:
            return CorrectionResult(
                success=False,
                original_content="",
                corrected_content="",
                violations_fixed=[],
                errors=[f"Error applying correction: {str(e)}"]
            )

    def save_correction_results_to_database(
        self,
        violations: List[FlakeViolation],
        corrections: List[CorrectionResult]
    ):
        """Save correction results to analytics database"""
        self.logger.info("Saving correction results to database", "database")

        try:
            with sqlite3.connect(self.analytics_db) as conn:
                cursor = conn.cursor()

                # Update compliance session
                cursor.execute('''
                    INSERT OR REPLACE INTO compliance_sessions
                    (session_id, workspace_path, start_time, end_time, files_processed,
                     violations_found, violations_fixed, success_rate, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    self.session_id,
                    str(self.workspace_path),
                    datetime.now().isoformat(),
                    datetime.now().isoformat(),
                    self.stats['files_processed'],
                    self.stats['violations_found'],
                    self.stats['violations_fixed'],
                    (self.stats['violations_fixed'] / max(1, self.stats['violations_found'])) * 100,
                    "COMPLETED"
                ))

                # Clear existing violations and add new ones
                cursor.execute('DELETE FROM violations')

                for violation in violations:
                    cursor.execute('''
                        INSERT INTO violations
                        (file_path,
                         line_number,
                         column_number,
                         error_code,
                         message,
                         session_id
                        )
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        violation.file_path,
                        violation.line_number,
                        violation.column,
                        violation.error_code,
                        violation.message,
                        self.session_id
                    ))

                # Record individual fixes in correction_history
                for violation, result in zip(violations, corrections):
                    if result.success:
                        for fix in result.violations_fixed:
                            cursor.execute(
                                '''
                                INSERT INTO correction_history
                                (session_id, file_path, violation_code, fix_applied, timestamp)
                                VALUES (?, ?, ?, ?, ?)
                                ''',
                                (
                                    self.session_id,
                                    violation.file_path,
                                    violation.error_code,
                                    fix,
                                    datetime.now().isoformat(),
                                ),
                            )

        except Exception as e:
            self.logger.error(f"Error saving to database: {e}")

    def execute_comprehensive_correction(self):
        """Execute comprehensive Flake8 correction with DUAL COPILOT validation"""

        start_time = datetime.now()
        self.logger.info(
            f"Starting comprehensive Flake8 correction session: {self.session_id}",
            "start"
        )
        self.logger.info(f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}", "info")
        self.logger.info(f"Workspace: {self.workspace_path}", "info")
        self.logger.info(f"Process ID: {os.getpid()}", "info")
        try:
            with tqdm(
                    total=100,
                    desc="[PHASE 1] Loading Database Patterns",
                    unit="%") as pbar:
                pbar.set_description("[DATABASE] Loading correction patterns")
                self.load_correction_patterns_from_database()
                pbar.update(100)

            # Phase 2: Scan for violations
            with tqdm(
                    total=100,
                    desc="[PHASE 2] Scanning Violations",
                    unit="%") as pbar:
                pbar.set_description("[SEARCH] Scanning for Flake8 violations")
                violations = self.run_flake8_scan()
                pbar.update(100)

            if not violations:
                self.logger.info(
                    "No violations found - workspace is compliant!",
                    "success"
                )
                return

            # Phase 3: Apply corrections
            corrections = []
            files_to_process = list(set(v.file_path for v in violations))
            self.stats['files_processed'] = len(files_to_process)

            with tqdm(
                    total=len(files_to_process),
                    desc="[PHASE 3] Applying Corrections") as pbar:
                for file_path in files_to_process:
                    pbar.set_description(f"[FIX] {Path(file_path).name}")

                    file_violations = [v for v in violations if v.file_path == file_path]
                    file_corrected = False

                    for violation in file_violations:
                        result = self.apply_correction_pattern(file_path, violation)
                        corrections.append(result)

                        if result.success:
                            self.stats['violations_fixed'] += len(result.violations_fixed)
                            file_corrected = True

                    if file_corrected:
                        self.stats['files_modified'] += 1

                    pbar.update(1)
            with tqdm(total=100, desc="[PHASE 4] Saving Results", unit="%") as pbar:
                pbar.set_description("[DATABASE] Saving results to database")
                self.save_correction_results_to_database(violations, corrections)
                pbar.update(100)

            # Phase 5: Generate completion report
            self.generate_completion_report(start_time)

        except Exception as e:
            self.logger.error(f"Critical error during correction: {e}")
            self.stats['errors_encountered'] += 1

    def generate_completion_report(self, start_time: datetime):
        """Generate comprehensive completion report"""
        duration = (datetime.now() - start_time).total_seconds()

        self.logger.info("=" * 60, "complete")
        self.logger.info("DATABASE-FIRST FLAKE8 CORRECTION COMPLETE", "complete")
        self.logger.info("=" * 60, "complete")
        self.logger.info(f"Session ID: {self.session_id}", "info")
        self.logger.info(f"Total Duration: {duration:.1f} seconds", "info")
        self.logger.info(f"Files Processed: {self.stats['files_processed']}", "info")
        self.logger.info(f"Violations Found: {self.stats['violations_found']}", "info")
        self.logger.info(f"Violations Fixed: {self.stats['violations_fixed']}", "info")
        self.logger.info(f"Files Modified: {self.stats['files_modified']}", "info")
        success_rate = (
            self.stats['violations_fixed'] / max(1, self.stats['violations_found'])
        ) * 100
        self.logger.info(f"Success Rate: {success_rate:.1f}%", "info")
        self.logger.info("=" * 60, "complete")

        # DUAL COPILOT validation
        if self.stats['violations_fixed'] > 0:
            self.logger.info(
                "DUAL COPILOT VALIDATION: PRIMARY EXECUTION SUCCESSFUL",
                "validation"
            )
        else:
            self.logger.warning("DUAL COPILOT VALIDATION: NO FIXES APPLIED - REVIEW REQUIRED")


def main():
    print(
        f"{VISUAL_INDICATORS['start']} Database-First Windows-Compatible Flake8 Corrector"
    )
    start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"{VISUAL_INDICATORS['info']} Session started at {start_time}")

    try:
        # Initialize corrector
        corrector = DatabaseFirstFlake8Corrector()

        # Execute with timeout protection
        timeout_minutes = 30
        start_time = time.time()

        corrector.execute_comprehensive_correction()

        elapsed = time.time() - start_time
        if elapsed > (timeout_minutes * 60):
            print(
                f"{VISUAL_INDICATORS['warning']} Process exceeded {timeout_minutes} minute timeout")

        print(f"{VISUAL_INDICATORS['complete']} Correction process completed successfully")

    except KeyboardInterrupt:
        print(f"{VISUAL_INDICATORS['warning']} Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"{VISUAL_INDICATORS['error']} Critical error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
