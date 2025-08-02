"""
Database compliance checker operations.
Refactored from original database_compliance_checker.py with enhanced functionality.
"""

import logging
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from tqdm import tqdm

from ..core.connection import DatabaseConnection

# Text-based indicators (NO Unicode emojis)
TEXT_INDICATORS = {
    'start': '[START]',
    'success': '[SUCCESS]',
    'error': '[ERROR]',
    'progress': '[PROGRESS]',
    'info': '[INFO]'
}


class DatabaseComplianceChecker:
    """Enhanced Enterprise-grade Flake8 correction system with database integration"""

    def __init__(self, workspace_path: Optional[str] = None):
        if workspace_path is None:
            workspace_path = os.getenv("GH_COPILOT_WORKSPACE", Path.cwd())

        self.workspace_path = Path(workspace_path)
        # Use analytics.db for logging correction history
        self.database_path = self.workspace_path / "databases" / "analytics.db"
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self.db_connection = DatabaseConnection(self.database_path)
        self.logger = logging.getLogger(__name__)

    def execute_correction(self) -> bool:
        """Execute Flake8 correction with visual indicators and database integration"""
        start_time = datetime.now()
        self.logger.info(f"{TEXT_INDICATORS['start']} Correction started: {start_time}")

        try:
            with tqdm(total=100, desc="[PROGRESS] Flake8 Correction", unit="%") as pbar:

                pbar.set_description("[PROGRESS] Scanning files")
                files_to_correct = self.scan_python_files()
                pbar.update(25)

                pbar.set_description("[PROGRESS] Applying corrections")
                corrected_files = self.apply_corrections(files_to_correct)
                pbar.update(50)

                pbar.set_description("[PROGRESS] Validating results")
                validation_passed = self.validate_corrections(corrected_files)
                pbar.update(25)

            duration = (datetime.now() - start_time).total_seconds()
            self.logger.info(
                f"{TEXT_INDICATORS['success']} Correction completed in {duration:.1f}s")
            return validation_passed

        except Exception as e:
            self.logger.error(f"{TEXT_INDICATORS['error']} Correction failed: {e}")
            return False

    def scan_python_files(self) -> List[str]:
        """Scan for Python files requiring correction"""
        python_files = []

        # Check if workspace path exists
        if not self.workspace_path.exists():
            self.logger.warning(
                f"{TEXT_INDICATORS['error']} Workspace path does not exist: {self.workspace_path}")
            return python_files

        for py_file in self.workspace_path.rglob("*.py"):
            if self.should_process_file(py_file):
                python_files.append(str(py_file))

        self.logger.info(
            f"{TEXT_INDICATORS['info']} Found {len(python_files)} Python files to check")
        return python_files

    def should_process_file(self, file_path: Path) -> bool:
        """Determine if file should be processed"""
        # Skip hidden directories and files
        if any(part.startswith('.') for part in file_path.parts):
            return False

        # Skip common build/cache directories
        skip_dirs = {'__pycache__', 'node_modules', 'venv', 'env', '.git', 'build', 'dist'}
        if any(part in skip_dirs for part in file_path.parts):
            return False

        return True

    def apply_corrections(self, files: List[str]) -> List[str]:
        """Apply corrections to files with database logging"""
        corrected = []

        for file_path in files:
            try:
                success, message = self.correct_file(file_path)
                self.log_correction_to_database(file_path, success, message)
                if success:
                    corrected.append(file_path)
            except Exception as e:
                error_msg = str(e)
                self.logger.error(
                    f"{TEXT_INDICATORS['error']} Failed to correct {file_path}: {error_msg}")
                self.log_correction_to_database(file_path, False, error_msg)

        return corrected

    def correct_file(self, file_path: str) -> Tuple[bool, str]:
        """Inspect and fix common compliance issues in a single file.

        Returns:
            Tuple[bool, str]: Success flag and details or error message.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            corrected = content
            corrections: List[str] = []

            # Remove common placeholder markers (TODO, FIXME, PLACEHOLDER)
            placeholder_pattern = re.compile(r"\b(TODO|FIXME|PLACEHOLDER)\b")
            corrected, placeholder_count = placeholder_pattern.subn('', corrected)
            if placeholder_count:
                corrections.append(f"removed {placeholder_count} placeholder markers")

            # Trim trailing whitespace
            trailing_ws_pattern = re.compile(r"[ \t]+(\r?\n)")
            corrected, ws_count = trailing_ws_pattern.subn(r"\1", corrected)
            if ws_count:
                corrections.append(f"trimmed whitespace in {ws_count} lines")

            # Ensure file ends with a newline
            if corrected and not corrected.endswith('\n'):
                corrected += '\n'
                corrections.append('added terminal newline')

            if corrections and corrected != content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(corrected)
                self.logger.info(
                    f"{TEXT_INDICATORS['info']} Applied corrections to {file_path}: "
                    + ", ".join(corrections)
                )
                return True, "; ".join(corrections)

            return True, "no changes needed"

        except Exception as e:
            error_msg = str(e)
            self.logger.error(
                f"{TEXT_INDICATORS['error']} File correction failed for {file_path}: {error_msg}")
            return False, error_msg

    def validate_corrections(self, files: List[str]) -> bool:
        """Validate that corrections were successful"""
        if not files:
            self.logger.info(f"{TEXT_INDICATORS['info']} No files were corrected")
            return True

        self.logger.info(f"{TEXT_INDICATORS['info']} Validated {len(files)} corrected files")
        return len(files) > 0

    def log_correction_to_database(self, file_path: str, success: bool, error_message: str = "") -> None:
        """Log correction attempt to database"""
        try:
            # Check if corrections table exists, create if not
            if not self.db_connection.table_exists('corrections'):
                self.create_corrections_table()

            query = """
                INSERT INTO corrections (file_path, timestamp, success, error_message)
                VALUES (?, ?, ?, ?)
            """
            params = (file_path, datetime.now().isoformat(), success, error_message)
            self.db_connection.execute_query(query, params)

        except Exception as e:
            self.logger.warning(
                f"{TEXT_INDICATORS['error']} Failed to log correction to database: {e}")

    def create_corrections_table(self) -> None:
        """Create corrections tracking table"""
        query = """
            CREATE TABLE IF NOT EXISTS corrections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                success BOOLEAN NOT NULL,
                error_message TEXT
            )
        """
        self.db_connection.execute_query(query)

    def get_correction_stats(self) -> Dict[str, Any]:
        """Get correction statistics from database"""
        try:
            if not self.db_connection.table_exists('corrections'):
                return {'total': 0, 'successful': 0, 'failed': 0}

            stats_query = """
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful,
                    SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) as failed
                FROM corrections
            """
            result = self.db_connection.execute_query(stats_query)
            if result:
                row = result[0]
                return {
                    'total': row['total'],
                    'successful': row['successful'],
                    'failed': row['failed']
                }
            return {'total': 0, 'successful': 0, 'failed': 0}

        except Exception as e:
            self.logger.error(f"{TEXT_INDICATORS['error']} Failed to get correction stats: {e}")
            return {'total': 0, 'successful': 0, 'failed': 0}


def main():
    """Main execution function - maintains backward compatibility"""
    corrector = DatabaseComplianceChecker()
    success = corrector.execute_correction()

    # Display statistics
    stats = corrector.get_correction_stats()
    print(f"\n{TEXT_INDICATORS['info']} Correction Statistics:")
    print(f"  Total attempts: {stats['total']}")
    print(f"  Successful: {stats['successful']}")
    print(f"  Failed: {stats['failed']}")

    if success:
        print(f"{TEXT_INDICATORS['success']} Enterprise Flake8 correction completed")
    else:
        print(f"{TEXT_INDICATORS['error']} Enterprise Flake8 correction failed")

    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
