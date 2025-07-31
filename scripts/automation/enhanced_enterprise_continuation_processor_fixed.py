#!/usr/bin/env python3
"""
🌟 ENHANCED ENTERPRISE CONTINUATION PROCESSOR
Advanced Violation Processing with Improved Database Schema Compatibility

Author: Enterprise Violation Processing System
Date: July 13, 2025
Status: PRODUCTION READY - ENHANCED DEPLOYMENT

ADVANCED FEATURES:
- Enhanced database schema compatibility
- Improved success rate patterns
- Advanced pattern matching algorithms
- Intelligent violation prioritization
- Comprehensive logging and monitoring
"""

import re
import sys
import sqlite3
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from tqdm import tqdm

# Configure enterprise logging with UTF-8 encoding
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("enhanced_enterprise_processing.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


class EnhancedEnterpriseProcessor:
    """🌟 Enhanced Enterprise Processor - Advanced Violation Processing"""

    def __init__(self, workspace_path: str = "e:/gh_COPILOT"):
        self.workspace_path = Path(workspace_path)
        self.database_path = self.workspace_path / "databases" / "flake8_violations.db"

        # CRITICAL: External backup root only
        self.backup_root = Path("e:/temp/gh_COPILOT_Enhanced_Backups")
        self.backup_root.mkdir(parents=True, exist_ok=True)

        # Validate environment
        self.validate_environment()

        # Enhanced violation categorization
        self.critical_violations = [
            "E999",  # SyntaxError
            "E902",  # IOError
            "F401",  # module imported but unused
            "F821",  # undefined name
            "F822",  # duplicate argument
            "F823",  # local variable referenced before assignment
        ]

        self.high_impact_violations = [
            "E501",  # line too long
            "W291",  # trailing whitespace
            "W293",  # blank line contains whitespace
            "E302",  # expected 2 blank lines
            "E303",  # too many blank lines
            "E304",  # blank lines found after function decorator
        ]

        self.standard_violations = [
            "W292",  # no newline at end of file
            "W391",  # blank line at end of file
            "E261",  # at least two spaces before inline comment
            "E262",  # inline comment should start with '# '
            "E265",  # block comment should start with '# '
        ]

        self.session_id = f"enhanced_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        logger.info("🌟 ENHANCED ENTERPRISE PROCESSOR INITIALIZED")
        logger.info(f"Session ID: {self.session_id}")
        logger.info(f"External Backup Root: {self.backup_root}")
        logger.info("Processing Mode: Enhanced Enterprise")

    def validate_environment(self):
        """🛡️ Enhanced environment validation with comprehensive checks"""
        validation_errors = []

        # Check for recursive backup folders
        workspace_backups = list(self.workspace_path.rglob("*backup*"))
        if workspace_backups:
            for backup in workspace_backups:
                validation_errors.append(f"Recursive backup detected: {backup}")

        # Validate database accessibility
        if not self.database_path.exists():
            logger.warning("⚠️ Database not found, will create if needed")
        else:
            try:
                with sqlite3.connect(self.database_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM violations LIMIT 1")
                    logger.info("✅ Database connection validated")
            except Exception as e:
                validation_errors.append(f"Database validation failed: {e}")

        # Validate external backup root
        if not str(self.backup_root).startswith("e:/temp/"):
            validation_errors.append(f"Invalid backup root: {self.backup_root}")

        # Check workspace permissions
        test_file = self.workspace_path / ".permission_test"
        try:
            test_file.write_text("test")
            test_file.unlink()
            logger.info("✅ Workspace write permissions validated")
        except Exception as e:
            validation_errors.append(f"Workspace permission error: {e}")

        if validation_errors:
            logger.error("🚨 CRITICAL: Environment validation failed:")
            for error in validation_errors:
                logger.error(f"   - {error}")
            raise RuntimeError("CRITICAL: Environment validation failed")

        logger.info("✅ Enhanced environment validation passed")

    def get_enhanced_batches(self, max_batches: int = 75) -> List[Dict]:
        """📊 Get enhanced batches with intelligent prioritization"""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()

                # Get critical violations first (highest priority)
                critical_violations = self._get_violations_by_type(cursor, self.critical_violations, max_batches * 5)

                # Get high impact violations
                high_impact_violations = self._get_violations_by_type(
                    cursor, self.high_impact_violations, max_batches * 10
                )

                # Get standard violations
                standard_violations = self._get_violations_by_type(cursor, self.standard_violations, max_batches * 15)

                # Combine and create batches
                all_violations = critical_violations + high_impact_violations + standard_violations
                batches = self._create_enhanced_batches(all_violations, max_batches)

                logger.info(f"📊 Created {len(batches)} enhanced batches")
                logger.info(f"🚨 Critical violations: {len(critical_violations)}")
                logger.info(f"⚡ High impact violations: {len(high_impact_violations)}")
                logger.info(f"📋 Standard violations: {len(standard_violations)}")

                return batches

        except Exception as e:
            logger.error(f"❌ Failed to get enhanced batches: {e}")
            return []

    def _get_violations_by_type(self, cursor: sqlite3.Cursor, violation_types: List[str], limit: int) -> List[Tuple]:
        """📋 Get violations by type with proper SQL handling"""
        if not violation_types:
            return []

        placeholders = ",".join(["?" for _ in violation_types])
        cursor.execute(
            f"""
            SELECT file_path, line_number, error_code, line_content,
                   COALESCE(error_description, '') as error_description
            FROM violations
            WHERE error_code IN ({placeholders})
            AND status = 'PENDING'
            ORDER BY error_code, file_path, line_number
            LIMIT ?
        """,
            tuple(violation_types) + (limit,),
        )

        return cursor.fetchall()

    def _create_enhanced_batches(self, violations: List[Tuple], max_batches: int) -> List[Dict]:
        """📦 Create enhanced batches with intelligent grouping"""
        batches = []
        current_batch = {}
        current_file = None

        for violation_data in violations:
            file_path = violation_data[0]
            line_number = violation_data[1]
            error_code = violation_data[2]
            line_content = violation_data[3]
            error_description = violation_data[4] if len(violation_data) > 4 else ""

            if file_path != current_file:
                if current_batch:
                    batches.append(current_batch)
                    if len(batches) >= max_batches:
                        break

                current_batch = {
                    "file_path": file_path,
                    "violations": [],
                    "critical_count": 0,
                    "high_impact_count": 0,
                    "standard_count": 0,
                    "priority_score": 0,
                }
                current_file = file_path

            violation_entry = {
                "line_number": line_number,
                "error_code": error_code,
                "line_content": line_content,
                "error_description": error_description,
            }

            current_batch["violations"].append(violation_entry)

            # Categorize and score
            if error_code in self.critical_violations:
                current_batch["critical_count"] += 1
                current_batch["priority_score"] += 10
            elif error_code in self.high_impact_violations:
                current_batch["high_impact_count"] += 1
                current_batch["priority_score"] += 5
            else:
                current_batch["standard_count"] += 1
                current_batch["priority_score"] += 1

        if current_batch and len(batches) < max_batches:
            batches.append(current_batch)

        # Sort batches by priority score (highest first)
        batches.sort(key=lambda x: x["priority_score"], reverse=True)

        return batches

    def apply_enhanced_fixes(self, batch: Dict) -> Tuple[int, int, List[str]]:
        """🔧 Apply enhanced fixes with advanced pattern matching"""
        file_path = batch["file_path"]
        violations = batch["violations"]

        try:
            # Create backup
            backup_path = self.create_enhanced_backup(file_path)

            # Read file with encoding detection
            content = self._read_file_safely(file_path)
            if content is None:
                logger.error(f"❌ Failed to read file: {file_path}")
                return 0, len(violations), []

            lines = content.splitlines(keepends=True)

            fixed_count = 0
            fixed_violations = []

            # Sort violations by line number (reverse order)
            sorted_violations = sorted(violations, key=lambda x: x["line_number"], reverse=True)

            # Apply enhanced fixes
            for violation in sorted_violations:
                line_idx = violation["line_number"] - 1

                if 0 <= line_idx < len(lines):
                    original_line = lines[line_idx]
                    fixed_line = self.apply_enhanced_fix(
                        original_line,
                        violation["error_code"],
                        violation.get("line_content", ""),
                        violation.get("error_description", ""),
                    )

                    if fixed_line != original_line:
                        lines[line_idx] = fixed_line
                        fixed_count += 1
                        fixed_violations.append(
                            {
                                "file_path": file_path,
                                "line_number": violation["line_number"],
                                "error_code": violation["error_code"],
                                "backup_path": backup_path,
                            }
                        )

            # Write fixed file
            self._write_file_safely(file_path, "".join(lines))

            # Update database
            self.update_violation_status_enhanced(fixed_violations, "FIXED")

            return fixed_count, len(violations), [str(backup_path)]

        except Exception as e:
            logger.error(f"❌ Failed to apply enhanced fixes to {file_path}: {e}")
            return 0, len(violations), []

    def _read_file_safely(self, file_path: str) -> Optional[str]:
        """📖 Read file with encoding detection and error handling"""
        encodings = ["utf-8", "utf-8-sig", "latin1", "cp1252"]

        for encoding in encodings:
            try:
                with open(file_path, "r", encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
            except Exception as e:
                logger.error(f"❌ Error reading {file_path} with {encoding}: {e}")
                continue

        logger.error(f"❌ Failed to read {file_path} with any encoding")
        return None

    def _write_file_safely(self, file_path: str, content: str):
        """📝 Write file with UTF-8 encoding and error handling"""
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            logger.error(f"❌ Failed to write {file_path}: {e}")
            raise

    def apply_enhanced_fix(
        self, line: str, error_code: str, line_content: str = "", error_description: str = ""
    ) -> str:
        """🎯 Apply enhanced fixes with advanced pattern matching"""
        if error_code == "W291":  # trailing whitespace
            return line.rstrip() + "\n" if line.endswith("\n") else line.rstrip()

        elif error_code == "W293":  # blank line contains whitespace
            if line.strip() == "":
                return "\n" if line.endswith("\n") else ""

        elif error_code == "W292":  # no newline at end of file
            if not line.endswith("\n"):
                return line + "\n"

        elif error_code == "W391":  # blank line at end of file
            return line.rstrip("\n")

        elif error_code == "E501":  # line too long
            return self._fix_long_line(line)

        elif error_code == "E302":  # expected 2 blank lines
            return "\n\n" + line

        elif error_code == "E303":  # too many blank lines
            if line.strip() == "":
                return ""

        elif error_code == "E304":  # blank lines found after function decorator
            if line.strip() == "":
                return ""

        elif error_code == "E261":  # at least two spaces before inline comment
            return re.sub(r"(\S)(\s*)#", r"\1  #", line)

        elif error_code == "E262":  # inline comment should start with '# '
            return re.sub(r"#([^\s])", r"# \1", line)

        elif error_code == "E265":  # block comment should start with '# '
            if line.strip().startswith("#") and not line.strip().startswith("# "):
                return re.sub(r"^(\s*)#([^\s])", r"\1# \2", line)

        elif error_code == "F401":  # module imported but unused
            # Simple removal for unused imports
            if "import" in line and not line.strip().startswith("#"):
                return ""

        return line

    def _fix_long_line(self, line: str) -> str:
        """🔧 Fix long lines with intelligent breaking"""
        if len(line) <= 79:
            return line

        # Try to break at logical points
        if "," in line and len(line) < 120:
            # Find good break point after comma
            break_point = line.rfind(",", 0, 75)
            if break_point > 50:
                indent = len(line) - len(line.lstrip())
                return line[: break_point + 1] + "\n" + " " * (indent + 4) + line[break_point + 1 :].lstrip()

        # Try to break at operators
        for op in [" and ", " or ", " + ", " - ", " * ", " / "]:
            if op in line:
                break_point = line.rfind(op, 0, 75)
                if break_point > 50:
                    indent = len(line) - len(line.lstrip())
                    return line[:break_point] + "\n" + " " * (indent + 4) + line[break_point:].lstrip()

        return line

    def update_violation_status_enhanced(self, fixes_applied: List[Dict], status: str):
        """📊 Update violation status with enhanced tracking"""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()

                for fix in fixes_applied:
                    cursor.execute(
                        """
                        UPDATE violations
                        SET status = ?, fixed_date = ?, processor_type = ?
                        WHERE file_path = ? AND line_number = ? AND error_code = ?
                    """,
                        (
                            status,
                            datetime.now().isoformat(),
                            "ENHANCED",
                            fix["file_path"],
                            fix["line_number"],
                            fix["error_code"],
                        ),
                    )

                conn.commit()
                logger.info(f"📊 Updated {len(fixes_applied)} violation statuses to {status}")

        except Exception as e:
            logger.error(f"❌ Failed to update violation status: {e}")

    def create_enhanced_backup(self, file_path: str) -> str:
        """💾 Create enhanced backup with metadata"""
        file_path_obj = Path(file_path)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{file_path_obj.stem}_enhanced_{timestamp}{file_path_obj.suffix}"
        backup_path = self.backup_root / backup_filename

        try:
            shutil.copy2(file_path, backup_path)

            # Create metadata file
            metadata_path = backup_path.with_suffix(backup_path.suffix + ".meta")
            metadata = {
                "original_path": str(file_path),
                "backup_timestamp": timestamp,
                "session_id": self.session_id,
                "processor_type": "ENHANCED",
                "file_size": file_path_obj.stat().st_size,
            }

            with open(metadata_path, "w", encoding="utf-8") as f:
                f.write(str(metadata))

            logger.info(f"💾 Created enhanced backup: {backup_path}")
            return str(backup_path)
        except Exception as e:
            logger.error(f"❌ Enhanced backup failed: {e}")
            return ""

    def execute_enhanced_processing(self, max_batches: int = 75) -> Dict[str, Any]:
        """🌟 Execute enhanced enterprise processing"""
        start_time = datetime.now()
        logger.info("🌟 STARTING ENHANCED ENTERPRISE PROCESSING")
        logger.info(f"Target: {max_batches} batches maximum")
        logger.info(f"Focus: Critical + High Impact + Standard violations")

        results = self._create_empty_results()

        try:
            # Get enhanced batches
            logger.info("📊 Getting enhanced violation batches...")
            batches = self.get_enhanced_batches(max_batches)

            if not batches:
                logger.warning("⚠️ No enhanced batches found")
                return results

            # Process batches with enhanced tracking
            total_fixed = 0
            total_attempted = 0
            all_backups = []
            critical_fixed = 0
            high_impact_fixed = 0
            standard_fixed = 0

            with tqdm(total=len(batches), desc="🌟 Enhanced Processing", unit="batch") as pbar:
                for i, batch in enumerate(batches):
                    pbar.set_description(f"🌟 Processing {Path(batch['file_path']).name}")

                    fixed_count, attempted_count, backups = self.apply_enhanced_fixes(batch)

                    total_fixed += fixed_count
                    total_attempted += attempted_count
                    all_backups.extend(backups)

                    # Track category fixes
                    critical_fixed += min(fixed_count, batch.get("critical_count", 0))
                    remaining = fixed_count - critical_fixed
                    high_impact_fixed += min(remaining, batch.get("high_impact_count", 0))
                    remaining -= high_impact_fixed
                    standard_fixed += min(remaining, batch.get("standard_count", 0))

                    # Update progress
                    pbar.update(1)
                    success_rate = (total_fixed / total_attempted * 100) if total_attempted > 0 else 0
                    pbar.set_postfix(
                        {
                            "Success": f"{success_rate:.1f}%",
                            "Fixed": total_fixed,
                            "Priority": batch.get("priority_score", 0),
                        }
                    )

            # Calculate final results
            duration = (datetime.now() - start_time).total_seconds()
            success_rate = (total_fixed / total_attempted * 100) if total_attempted > 0 else 0

            results.update(
                {
                    "session_id": self.session_id,
                    "batches_processed": len(batches),
                    "violations_fixed": total_fixed,
                    "violations_attempted": total_attempted,
                    "critical_violations_fixed": critical_fixed,
                    "high_impact_violations_fixed": high_impact_fixed,
                    "standard_violations_fixed": standard_fixed,
                    "success_rate": success_rate,
                    "processing_duration": duration,
                    "backups_created": len(all_backups),
                    "backup_paths": all_backups,
                    "processing_type": "ENHANCED_ENTERPRISE",
                    "status": "COMPLETED_SUCCESS" if success_rate >= 85 else "COMPLETED_PARTIAL",
                }
            )

            # Log final summary
            logger.info("✅ ENHANCED ENTERPRISE PROCESSING COMPLETED")
            logger.info(f"📊 Success Rate: {success_rate:.1f}%")
            logger.info(f"🔧 Fixed: {total_fixed}/{total_attempted} violations")
            logger.info(
                f"🚨 Critical: {critical_fixed}, ⚡ High Impact: {high_impact_fixed}, 📋 Standard: {standard_fixed}"
            )
            logger.info(f"⏱️ Duration: {duration:.1f} seconds")
            logger.info(f"💾 Backups: {len(all_backups)} created")

            return results

        except Exception as e:
            logger.error(f"❌ Enhanced processing failed: {e}")
            results["status"] = "FAILED"
            results["error"] = str(e)
            return results

    def _create_empty_results(self) -> Dict[str, Any]:
        """📊 Create empty results structure"""
        return {
            "session_id": self.session_id,
            "batches_processed": 0,
            "violations_fixed": 0,
            "violations_attempted": 0,
            "critical_violations_fixed": 0,
            "high_impact_violations_fixed": 0,
            "standard_violations_fixed": 0,
            "success_rate": 0.0,
            "processing_duration": 0.0,
            "backups_created": 0,
            "backup_paths": [],
            "processing_type": "ENHANCED_ENTERPRISE",
            "status": "INITIALIZED",
        }


def main():
    """🌟 Main enhanced processing execution"""
    try:
        processor = EnhancedEnterpriseProcessor()
        results = processor.execute_enhanced_processing(max_batches=75)

        print("=" * 80)
        print("🌟 ENHANCED ENTERPRISE PROCESSING COMPLETE")
        print("=" * 80)
        print(f"Session ID: {results['session_id']}")
        print(f"Status: {results['status']}")
        print(f"Success Rate: {results['success_rate']:.1f}%")
        print(f"Violations Fixed: {results['violations_fixed']}")
        print(f"Critical Fixed: {results['critical_violations_fixed']}")
        print(f"High Impact Fixed: {results['high_impact_violations_fixed']}")
        print(f"Standard Fixed: {results['standard_violations_fixed']}")
        print(f"Batches Processed: {results['batches_processed']}")
        print(f"Duration: {results['processing_duration']:.1f} seconds")
        print(f"Backups Created: {results['backups_created']}")
        print("=" * 80)

        return results["status"] == "COMPLETED_SUCCESS"

    except Exception as e:
        logger.error(f"❌ Main execution failed: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
