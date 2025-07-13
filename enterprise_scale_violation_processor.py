#!/usr/bin/env python3
"""
🏢 ENTERPRISE SCALE VIOLATION PROCESSOR
Large-Scale Automated Violation Processing with Full Monitoring and Safety Measures

Author: Enterprise Violation Processing System
Date: July 13, 2025
Status: PRODUCTION READY - ENTERPRISE DEPLOYMENT

SAFETY FEATURES:
- Comprehensive backup system before all modifications
- Anti-recursion protection with workspace validation
- Real-time monitoring with alert thresholds
- Progressive batch processing with rollback capabilities
- Unicode-compatible processing with UTF-8 encoding
- Session-based logging with comprehensive audit trails
"""

import os
import sys
import json
import sqlite3
import shutil
import logging
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from tqdm import tqdm
import time

# Configure enterprise logging with UTF-8 encoding
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enterprise_scale_processing.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class ProcessingSession:
    """📊 Processing session data structure"""
    session_id: str
    start_time: datetime
    target_violations: int
    processing_mode: str
    batch_size: int
    safety_level: str


@dataclass
class ProcessingBatch:
    """📦 Processing batch data structure"""
    batch_id: str
    file_path: str
    violations: List[Dict]
    priority: str
    estimated_fixes: int
    backup_created: bool = False
    processing_status: str = 'pending'


@dataclass
class ProcessingResults:
    """📈 Processing results data structure"""
    session_id: str
    total_violations_processed: int
    successful_fixes: int
    failed_fixes: int
    skipped_violations: int
    files_processed: int
    batches_completed: int
    processing_time: float
    health_score_improvement: float


class EnterpriseScaleViolationProcessor:
    """🏢 Enterprise-Scale Violation Processing Engine with Full Safety Measures"""

    def __init__(self, workspace_path: str = "e:/gh_COPILOT"):
        # CRITICAL: Environment validation and anti-recursion protection
        self.validate_enterprise_environment()

        self.workspace_path = Path(workspace_path)
        self.database_path = self.workspace_path / "databases" / "flake8_violations.db"
        self.monitoring_path = self.workspace_path / "monitoring"
        self.backup_root = self.workspace_path / "enterprise_backups"

        # Create essential directories
        self.monitoring_path.mkdir(exist_ok=True)
        self.backup_root.mkdir(exist_ok=True)

        # Processing configuration
        self.batch_size = 25  # Conservative batch size for safety
        self.max_concurrent_files = 5  # Limit concurrent processing
        self.safety_level = "ENTERPRISE"  # Maximum safety protocols
        self.rollback_enabled = True

        # Alert thresholds for enterprise monitoring
        self.alert_thresholds = {
            'max_failures_per_batch': 5,
            'min_success_rate': 0.75,  # 75% minimum success rate
            'max_processing_time': 300,  # 5 minutes per batch
            'critical_violation_threshold': 10
        }

        # Initialize processing session
        self.session_id = f"enterprise_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        logger.info("🏢 ENTERPRISE SCALE VIOLATION PROCESSOR INITIALIZED")
        logger.info(f"Session ID: {self.session_id}")
        logger.info(f"Database: {self.database_path}")
        logger.info(f"Monitoring: {self.monitoring_path}")
        logger.info(f"Backup Root: {self.backup_root}")

    def validate_enterprise_environment(self):
        """🛡️ CRITICAL: Validate enterprise environment with anti-recursion protection"""
        workspace_root = Path(os.getcwd())

        # MANDATORY: Check for recursive backup folders
        forbidden_patterns = ['*backup*', '*_backup_*', 'backups', '*temp*']
        violations = []

        for pattern in forbidden_patterns:
            for folder in workspace_root.rglob(pattern):
                if folder.is_dir() and folder != workspace_root:
                    violations.append(str(folder))

        if violations:
            logger.error("🚨 CRITICAL: Recursive folder violations detected!")
            for violation in violations:
                logger.error(f"   - {violation}")
            raise RuntimeError("CRITICAL: Recursive violations prevent enterprise execution")

        # MANDATORY: Validate proper environment root
        proper_root = "gh_COPILOT"
        if not str(workspace_root).endswith(proper_root):
            logger.warning(f"⚠️ Non-standard workspace root: {workspace_root}")

        logger.info("✅ ENTERPRISE ENVIRONMENT VALIDATION PASSED")

    def get_pending_violations(self) -> List[Dict]:
        """📊 Get all pending violations from database"""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT id, file_path, line_number, column_number, error_code, message, status
                    FROM violations 
                    WHERE status = 'pending'
                    ORDER BY 
                        CASE 
                            WHEN error_code LIKE 'F8%' THEN 1  -- Critical
                            WHEN error_code LIKE 'E%' THEN 2   -- High
                            WHEN error_code LIKE 'W%' THEN 3   -- Medium
                            ELSE 4                              -- Low
                        END,
                        file_path, line_number
                """)

                violations = []
                for row in cursor.fetchall():
                    violations.append({
                        'id': row[0],
                        'file_path': row[1],
                        'line_number': row[2],
                        'column_number': row[3],
                        'error_code': row[4],
                        'message': row[5],
                        'status': row[6]
                    })

                logger.info(f"📊 Retrieved {len(violations)} pending violations")
                return violations

        except Exception as e:
            logger.error(f"❌ Error retrieving violations: {e}")
            return []

    def create_processing_batches(self, violations: List[Dict]) -> List[ProcessingBatch]:
        """📦 Create processing batches organized by file and priority"""
        file_violations = {}

        # Group violations by file
        for violation in violations:
            file_path = violation['file_path']
            if file_path not in file_violations:
                file_violations[file_path] = []
            file_violations[file_path].append(violation)

        batches = []
        batch_counter = 1

        # Create batches with priority classification
        for file_path, file_viols in file_violations.items():
            # Determine priority based on violation types
            critical_count = len([v for v in file_viols if v['error_code'].startswith('F8')])
            high_count = len([v for v in file_viols if v['error_code'].startswith('E')])

            if critical_count > 0:
                priority = "CRITICAL"
            elif high_count > len(file_viols) * 0.5:
                priority = "HIGH"
            elif len(file_viols) > 20:
                priority = "MEDIUM"
            else:
                priority = "LOW"

            # Estimate fixable violations (conservative estimate)
            fixable_types = [
    'W293',
    'E501',
    'E302',
    'F401',
    'W291',
    'W292',
    'E303',
    'E305',
    'W391',
     'E201']
            estimated_fixes = len([v for v in file_viols if v['error_code'] in fixable_types])

            batch = ProcessingBatch(
                batch_id=f"batch_{batch_counter:04d}",
                file_path=file_path,
                violations=file_viols,
                priority=priority,
                estimated_fixes=estimated_fixes
            )

            batches.append(batch)
            batch_counter += 1

        # Sort batches by priority
        priority_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        batches.sort(
    key=lambda b: (
        priority_order.get(
            b.priority, 4), len(
                b.violations)), reverse=True)

        logger.info(f"📦 Created {len(batches)} processing batches")
        logger.info(f"Priority breakdown: CRITICAL: {len([b for b in batches if b.priority == 'CRITICAL'])}, "
                    f"HIGH: {len([b for b in batches if b.priority == 'HIGH'])}, "
                    f"MEDIUM: {len([b for b in batches if b.priority == 'MEDIUM'])}, "
                    f"LOW: {len([b for b in batches if b.priority == 'LOW'])}")

        return batches

    def create_enterprise_backup(self, file_path: str) -> str:
        """💾 Create enterprise-grade backup with timestamp and validation"""
        try:
            source_path = Path(file_path)
            if not source_path.exists():
                raise FileNotFoundError(f"Source file not found: {source_path}")

            # Create timestamped backup directory
            backup_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_dir = self.backup_root / f"session_{self.session_id}" / backup_timestamp
            backup_dir.mkdir(parents=True, exist_ok=True)

            # Create backup file path maintaining directory structure
            relative_path = source_path.relative_to(self.workspace_path)
            backup_file_path = backup_dir / relative_path
            backup_file_path.parent.mkdir(parents=True, exist_ok=True)

            # Copy file with metadata preservation
            shutil.copy2(source_path, backup_file_path)

            # Verify backup integrity
            if backup_file_path.exists() and backup_file_path.stat().st_size == source_path.stat().st_size:
                logger.info(f"💾 Enterprise backup created: {backup_file_path}")
                return str(backup_file_path)
            else:
                raise RuntimeError("Backup integrity verification failed")

        except Exception as e:
            logger.error(f"❌ Backup creation failed for {file_path}: {e}")
            raise

    def apply_automated_fixes(self, batch: ProcessingBatch) -> Tuple[int, int, List[str]]:
        """🔧 Apply automated fixes to violations in batch with safety measures"""
        successful_fixes = 0
        failed_fixes = 0
        fix_details = []

        try:
            # Create enterprise backup
            backup_path = self.create_enterprise_backup(batch.file_path)
            batch.backup_created = True

            # Read file content
            with open(batch.file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            original_lines = lines.copy()
            fixes_applied = []

            # Process violations by type (safest types first)
            safe_violation_types = ['W293', 'W291', 'W292', 'W391', 'E201']
            moderate_violation_types = ['E302', 'E303', 'E305']
            complex_violation_types = ['E501', 'F401']

            processing_order = safe_violation_types + moderate_violation_types + complex_violation_types

            for violation_type in processing_order:
                type_violations = [v for v in batch.violations if v['error_code'] == violation_type]

                for violation in sorted(
                    type_violations, key=lambda x: x['line_number'], reverse=True):
                    try:
                        line_idx = violation['line_number'] - 1
                        if 0 <= line_idx < len(lines):
                            original_line = lines[line_idx]
                            fixed_line = self.fix_violation_line(original_line, violation)

                            if fixed_line != original_line:
                                lines[line_idx] = fixed_line
                                successful_fixes += 1
                                fixes_applied.append({
                                    'violation_id': violation['id'],
                                    'line_number': violation['line_number'],
                                    'error_code': violation['error_code'],
                                    'original': original_line.strip(),
                                    'fixed': fixed_line.strip()
                                })
                                fix_details.append(
    f"Fixed {
        violation['error_code']} at line {
            violation['line_number']}")
                            else:
                                failed_fixes += 1
                                fix_details.append(
    f"Could not fix {
        violation['error_code']} at line {
            violation['line_number']}")
                        else:
                            failed_fixes += 1
                            fix_details.append(
    f"Invalid line number {
        violation['line_number']} for {
            violation['error_code']}")

                    except Exception as e:
                        failed_fixes += 1
                        fix_details.append(
    f"Error fixing {
        violation.get(
            'error_code',
            'unknown')} at line {
                violation.get(
                    'line_number',
                    'unknown')}: {
                        str(e)}")

            # Write fixed content if any fixes were applied
            if successful_fixes > 0:
                with open(batch.file_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)

                # Update database with successful fixes
                self.update_violation_status(fixes_applied, 'fixed')

                logger.info(f"✅ Applied {successful_fixes} fixes to {batch.file_path}")
            else:
                logger.info(f"ℹ️ No fixes applied to {batch.file_path}")

            return successful_fixes, failed_fixes, fix_details

        except Exception as e:
            logger.error(f"❌ Error processing batch {batch.batch_id}: {e}")
            # Attempt rollback if backup exists
            if batch.backup_created:
                try:
                    shutil.copy2(backup_path, batch.file_path)
                    logger.info(f"🔄 Rolled back {batch.file_path} from backup")
                except Exception as rollback_error:
                    logger.error(f"❌ Rollback failed: {rollback_error}")

            return 0, len(batch.violations), [f"Batch processing failed: {str(e)}"]

    def fix_violation_line(self, line: str, violation: Dict) -> str:
        """🔧 Fix individual violation in line (conservative approach)"""
        error_code = violation['error_code']

        try:
            if error_code == 'W293':  # Blank line contains whitespace
                if line.strip() == '':
                    return '\n'

            elif error_code == 'W291':  # Trailing whitespace
                return line.rstrip() + '\n' if line.endswith('\n') else line.rstrip()

            elif error_code == 'W292':  # No newline at end of file
                if not line.endswith('\n'):
                    return line + '\n'

            elif error_code == 'W391':  # Blank line at end of file
                if line.strip() == '':
                    return ''

            elif error_code == 'E201':  # Whitespace after '('
                return line.replace('( ', '(')

            elif error_code == 'E302':  # Expected 2 blank lines
                if line.strip() and not line.startswith(' '):
                    return '\n\n' + line

            elif error_code == 'E303':  # Too many blank lines
                if line.strip() == '':
                    return ''

            elif error_code == 'E305':  # Expected 2 blank lines after class/function
                if line.strip() and ('def ' in line or 'class ' in line):
                    return '\n\n' + line

            # More complex fixes (conservative approach)
            elif error_code == 'E501':  # Line too long
                if len(line) > 79 and '=' in line and 'import' not in line:
                    # Simple case: split at assignment
                    parts = line.split('=', 1)
                    if len(parts) == 2 and len(parts[0].strip()) < 40:
                        return f"{parts[0].strip()} = \\\n    {parts[1].strip()}\n"

            elif error_code == 'F401':  # Imported but unused
                if 'import' in line and not line.strip().startswith('#'):
                    # Only remove simple import lines (conservative)
                    if line.strip().startswith('import ') or line.strip().startswith('from '):
                        return ''

        except Exception as e:
            logger.warning(f"⚠️ Could not fix {error_code}: {e}")

        return line  # Return original line if no fix applied

    def update_violation_status(self, fixes_applied: List[Dict], status: str):
        """📝 Update violation status in database"""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()

                for fix in fixes_applied:
                    cursor.execute("""
                        UPDATE violations 
                        SET status = ?, 
                            fixed_date = datetime('now'),
                            fix_details = ?
                        WHERE id = ?
                    """, (status, json.dumps(fix), fix['violation_id']))

                conn.commit()
                logger.info(f"📝 Updated {len(fixes_applied)} violation statuses to '{status}'")

        except Exception as e:
            logger.error(f"❌ Error updating violation status: {e}")

    def monitor_processing_health(self, current_batch: int, total_batches: int, 
                                  successful_fixes: int, failed_fixes: int, 
                                  processing_time: float) -> Dict[str, Any]:
        """📊 Monitor processing health and trigger alerts if needed"""
        success_rate = successful_fixes / \
            (successful_fixes + failed_fixes) if (successful_fixes + failed_fixes) > 0 else 0
        progress_percentage = (current_batch / total_batches) * 100

        health_metrics = {
            'progress_percentage': progress_percentage,
            'success_rate': success_rate,
            'successful_fixes': successful_fixes,
            'failed_fixes': failed_fixes,
            'processing_time': processing_time,
            'health_status': 'HEALTHY'
        }

        # Check alert thresholds
        alerts = []

        if success_rate < self.alert_thresholds['min_success_rate']:
            alerts.append(
    f"LOW_SUCCESS_RATE: {
        success_rate:.2%} < {
            self.alert_thresholds['min_success_rate']:.2%}")
            health_metrics['health_status'] = 'WARNING'

        if processing_time > self.alert_thresholds['max_processing_time']:
            alerts.append(
    f"SLOW_PROCESSING: {
        processing_time:.1f}s > {
            self.alert_thresholds['max_processing_time']}s")
            health_metrics['health_status'] = 'WARNING'

        if failed_fixes > self.alert_thresholds['max_failures_per_batch']:
            alerts.append(f"HIGH_FAILURE_RATE: {failed_fixes} failures in batch")
            health_metrics['health_status'] = 'CRITICAL'

        health_metrics['alerts'] = alerts

        if alerts:
            for alert in alerts:
                logger.warning(f"🚨 HEALTH ALERT: {alert}")

        return health_metrics

    def generate_processing_report(self, session: ProcessingSession, 
                                   results: ProcessingResults, 
                                   batches: List[ProcessingBatch]) -> str:
        """📋 Generate comprehensive processing report"""
        report = {
            'session_info': {
                'session_id': session.session_id,
                'start_time': session.start_time.isoformat(),
                'end_time': datetime.now().isoformat(),
                'processing_mode': session.processing_mode,
                'safety_level': session.safety_level
            },
            'processing_results': {
                'total_violations_processed': results.total_violations_processed,
                'successful_fixes': results.successful_fixes,
                'failed_fixes': results.failed_fixes,
                'skipped_violations': results.skipped_violations,
                'files_processed': results.files_processed,
                'batches_completed': results.batches_completed,
                'processing_time_seconds': results.processing_time,
                'success_rate': results.successful_fixes / results.total_violations_processed if results.total_violations_processed > 0 else 0,
                'health_score_improvement': results.health_score_improvement
            },
            'batch_summary': {
                'total_batches': len(batches),
                'critical_batches': len([b for b in batches if b.priority == 'CRITICAL']),
                'high_priority_batches': len([b for b in batches if b.priority == 'HIGH']),
                'medium_priority_batches': len([b for b in batches if b.priority == 'MEDIUM']),
                'low_priority_batches': len([b for b in batches if b.priority == 'LOW']),
                'completed_batches': len([b for b in batches if b.processing_status == 'completed']),
                'failed_batches': len([b for b in batches if b.processing_status == 'failed'])
            },
            'system_metrics': {
                'backup_system_used': True,
                'rollback_enabled': self.rollback_enabled,
                'safety_level': self.safety_level,
                'monitoring_active': True,
                'alert_thresholds_configured': len(self.alert_thresholds)
            }
        }

        # Save report to file
        report_path = self.monitoring_path / f"enterprise_processing_report_{self.session_id}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        logger.info(f"📋 Enterprise processing report saved: {report_path}")
        return str(report_path)

    def execute_enterprise_scale_processing(self, max_batches: Optional[int] = None,
                                            priority_filter: Optional[str] = None) -> ProcessingResults:
        """🚀 Execute enterprise-scale violation processing with full monitoring"""

        # MANDATORY: Start time and process tracking
        start_time = datetime.now()
        process_id = os.getpid()
        logger.info("="*80)
        logger.info("🏢 ENTERPRISE SCALE VIOLATION PROCESSING STARTED")
        logger.info("="*80)
        logger.info(f"🚀 Session ID: {self.session_id}")
        logger.info(f"🕐 Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"🆔 Process ID: {process_id}")
        logger.info(f"💾 Safety Level: {self.safety_level}")
        logger.info(f"🔄 Rollback Enabled: {self.rollback_enabled}")

        try:
            # Get pending violations
            with tqdm(total=100, desc="🔍 Discovering Violations", unit="%") as pbar:
                pbar.set_description("📊 Retrieving pending violations")
                pending_violations = self.get_pending_violations()
                pbar.update(50)

                pbar.set_description("📦 Creating processing batches")
                processing_batches = self.create_processing_batches(pending_violations)
                pbar.update(50)

            # Apply filters
            if priority_filter:
                processing_batches = [
    b for b in processing_batches if b.priority == priority_filter]
                logger.info(
    f"🎯 Filtered to {
        len(processing_batches)} {priority_filter} priority batches")

            if max_batches:
                processing_batches = processing_batches[:max_batches]
                logger.info(f"📊 Limited to first {max_batches} batches")

            # Initialize session and results
            session = ProcessingSession(
                session_id=self.session_id,
                start_time=start_time,
                target_violations=len(pending_violations),
                processing_mode="ENTERPRISE_SCALE",
                batch_size=self.batch_size,
                safety_level=self.safety_level
            )

            total_successful_fixes = 0
            total_failed_fixes = 0
            total_violations_processed = 0
            files_processed = 0
            batches_completed = 0

            # Process batches with comprehensive monitoring
            with tqdm(total=len(processing_batches), desc="🔄 Processing Batches", unit="batch") as pbar:

                for batch_idx, batch in enumerate(processing_batches):
                    batch_start_time = time.time()

                    # Update progress description
                    pbar.set_description(f"🔧 Processing {batch.priority} batch {batch.batch_id}")

                    try:
                        # Apply automated fixes with safety measures
                        successful_fixes, failed_fixes, fix_details = self.apply_automated_fixes(
                            batch)

                        # Update batch status
                        batch.processing_status = 'completed' if successful_fixes > 0 or failed_fixes == 0 else 'partial'

                        # Update totals
                        total_successful_fixes += successful_fixes
                        total_failed_fixes += failed_fixes
                        total_violations_processed += len(batch.violations)
                        files_processed += 1
                        batches_completed += 1

                        # Calculate batch processing time
                        batch_processing_time = time.time() - batch_start_time

                        # Monitor processing health
                        health_metrics = self.monitor_processing_health(
                            batch_idx + 1, len(processing_batches),
                            total_successful_fixes, total_failed_fixes,
                            batch_processing_time
                        )

                        # Update progress bar with health metrics
                        success_rate = total_successful_fixes / \
                            (total_successful_fixes +
    total_failed_fixes) if (total_successful_fixes +
     total_failed_fixes) > 0 else 0
                        pbar.set_postfix({
                            'Fixes': total_successful_fixes,
                            'Success Rate': f"{success_rate:.1%}",
                            'Health': health_metrics['health_status']
                        })

                        # Log batch completion
                        logger.info(
    f"✅ Batch {
        batch.batch_id} completed: {successful_fixes} fixes, {failed_fixes} failures")

                        # Critical health check - halt if too many failures
                        if health_metrics['health_status'] == 'CRITICAL' and batch_idx > 5:
                            logger.error("🚨 CRITICAL HEALTH STATUS - Halting processing for safety")
                            break

                    except Exception as e:
                        logger.error(f"❌ Batch {batch.batch_id} failed: {e}")
                        batch.processing_status = 'failed'
                        total_failed_fixes += len(batch.violations)
                        total_violations_processed += len(batch.violations)

                    pbar.update(1)

            # Calculate final metrics
            processing_time = (datetime.now() - start_time).total_seconds()
            health_score_improvement = (
    total_successful_fixes / len(pending_violations)) * 100 if pending_violations else 0

            # Create final results
            results = ProcessingResults(
                session_id=self.session_id,
                total_violations_processed=total_violations_processed,
                successful_fixes=total_successful_fixes,
                failed_fixes=total_failed_fixes,
                skipped_violations=len(pending_violations) - total_violations_processed,
                files_processed=files_processed,
                batches_completed=batches_completed,
                processing_time=processing_time,
                health_score_improvement=health_score_improvement
            )

            # Generate comprehensive report
            report_path = self.generate_processing_report(session, results, processing_batches)

            # Final logging
            logger.info("="*80)
            logger.info("✅ ENTERPRISE SCALE PROCESSING COMPLETED")
            logger.info("="*80)
            logger.info(f"📊 Total Violations Processed: {total_violations_processed}")
            logger.info(f"✅ Successful Fixes: {total_successful_fixes}")
            logger.info(f"❌ Failed Fixes: {total_failed_fixes}")
            logger.info(f"📁 Files Processed: {files_processed}")
            logger.info(f"📦 Batches Completed: {batches_completed}")
            logger.info(f"⏱️ Processing Time: {processing_time:.2f} seconds")
            logger.info(f"📈 Health Score Improvement: {health_score_improvement:.2f}%")
            logger.info(f"📋 Report: {report_path}")
            logger.info("="*80)

            return results

        except Exception as e:
            logger.error(f"❌ Enterprise processing failed: {e}")
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            raise


def main():
    """🏢 Main enterprise processing execution"""
    try:
        # Initialize enterprise processor
        processor = EnterpriseScaleViolationProcessor()

        # Execute enterprise-scale processing
        # Start with CRITICAL priority only for safety
        results = processor.execute_enterprise_scale_processing(
            max_batches=50,  # Process first 50 batches for safety
            priority_filter="CRITICAL"  # Start with critical violations only
        )

        print(f"\n🎉 Enterprise processing completed successfully!")
        print(f"✅ {results.successful_fixes} violations fixed")
        print(f"📈 {results.health_score_improvement:.2f}% health improvement")

        # Ask for continuation if more batches remain
        remaining_violations = results.total_violations_processed - results.successful_fixes
        if remaining_violations > 0:
            print(f"\n📊 {remaining_violations} violations remain for processing")
            print(f"🚀 Ready to process HIGH, MEDIUM, and LOW priority batches")

    except Exception as e:
        logger.error(f"❌ Main execution failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
