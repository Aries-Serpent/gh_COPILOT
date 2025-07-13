#!/usr/bin/env python3
"""""""
🔄 DATABASE CLEANUP PROCESSOR
Update violation status for already-fixed violations

Author: Enterprise Violation Processing System
Date: July 13, 2025
Status: DATABASE CLEANUP MODE

PURPOSE:
    - Scan pending violations and check if they're actually already fixed'
- Update database status for violations that no longer exist in files
- Provide accurate violation counts for future processing
"""""""

import os
import sys
import sqlite3
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Tuple
from tqdm import tqdm

# Configure cleanup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('database_cleanup.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class DatabaseCleanupProcessor:
    """🔄 Database cleanup processor for accurate violation tracking"""

    def __init__(self, workspace_path: str = "e:/gh_COPILOT"):
        self.workspace_path = Path(workspace_path)
        self.database_path = self.workspace_path / "databases" / "flake8_violations.db"

        logger.info("🔄 DATABASE CLEANUP PROCESSOR INITIALIZED")
        logger.info(f"Database: {self.database_path}")

    def get_pending_violations(self, limit: int = 1000) -> List[Tuple]:
        """📋 Get pending violations for verification"""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()

                cursor.execute("""""""
                    SELECT id, file_path, line_number, error_code, message
                    FROM violations
                    WHERE status = 'pending' AND error_code IN ('W291', 'W293')
                    ORDER BY file_path, line_number
                    LIMIT ?
                """, (limit,))""""

                return cursor.fetchall()

        except Exception as e:
            logger.error(f"❌ Database query error: {e}")
            return []

    def check_violation_still_exists(
        self, file_path: str, line_number: int, error_code: str) -> bool:
        """✅ Check if violation still exists in file"""
        try:
            if not Path(file_path).exists():
                return False  # File doesn't exist, violation is "fixed"'

            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            if line_number > len(lines) or line_number <= 0:
                return False  # Line doesn't exist, violation is "fixed"'

            line_content = lines[line_number - 1]

            if error_code == 'W291':  # Trailing whitespace
                # Check if line has trailing whitespace (excluding newline)
                line_without_newline = line_content.rstrip('\n')
                return line_without_newline != line_without_newline.rstrip()

            elif error_code == 'W293':  # Blank line contains whitespace
                # Check if blank line contains whitespace
                return line_content.strip() == '' and line_content.rstrip('\n') != ''

            return True  # Unknown error code, assume it still exists

        except Exception as e:
            logger.warning(f"⚠️ Error checking file {file_path}:{line_number}: {e}")
            return True  # If we can't check, assume it still exists'

    def update_violation_status(self, violation_ids: List[int], status: str) -> int:
        """📝 Update violation status in database"""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()

                # Convert list to comma-separated string for IN clause
                placeholders = ','.join('?' * len(violation_ids))
                query = f"UPDATE violations SET status = ? WHERE id IN ({placeholders})"

                cursor.execute(query, [status] + violation_ids)
                conn.commit()

                return cursor.rowcount

        except Exception as e:
            logger.error(f"❌ Database update error: {e}")
            return 0

    def execute_cleanup(self, batch_size: int = 1000) -> Dict[str, Any]:
        """🔄 Execute database cleanup process"""

        start_time = datetime.now()
        process_id = os.getpid()

        logger.info("="*80)
        logger.info("🔄 DATABASE CLEANUP PROCESSING STARTED")
        logger.info("="*80)
        logger.info(f"🕐 Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"🆔 Process ID: {process_id}")
        logger.info(f"📦 Batch Size: {batch_size}")

        try:
            # Get pending violations in batches
            total_checked = 0
            total_already_fixed = 0
            total_still_pending = 0
            files_processed = set()

            while True:
                # Get next batch of pending violations
                with tqdm(total=100, desc="📋 Loading violations", unit="%") as pbar:
                    pending_violations = self.get_pending_violations(batch_size)
                    pbar.update(100)

                if not pending_violations:
                    logger.info("✅ No more pending violations to process")
                    break

                logger.info(f"📦 Processing batch of {len(pending_violations)} violations")

                # Check each violation
                already_fixed_ids = []
                still_pending_ids = []

                with tqdm(total=len(pending_violations), desc=""search" Checking violations", unit="violation") as pbar:

                    for violation in pending_violations:
                        violation_id, file_path, line_number, error_code, message = violation

                        # Update progress description
                        file_name = Path(file_path).name[:30]
                        pbar.set_description(f""search" Checking {file_name}:{line_number}")

                        # Check if violation still exists
                        still_exists = self.check_violation_still_exists(
                            file_path, line_number, error_code)

                        if still_exists:
                            still_pending_ids.append(violation_id)
                            total_still_pending += 1
                        else:
                            already_fixed_ids.append(violation_id)
                            total_already_fixed += 1

                        total_checked += 1
                        files_processed.add(file_path)

                        pbar.update(1)
                        pbar.set_postfix({
                            'Fixed': total_already_fixed,
                            'Pending': total_still_pending,
                            'Rate': f"{total_already_fixed/total_checked:.1%}" if total_checked > 0 else "0%"
                        })

                # Update database for already-fixed violations
                if already_fixed_ids:
                    updated_count = self.update_violation_status(already_fixed_ids, 'fixed')
                    logger.info(f"✅ Updated {updated_count} violations to 'fixed' status")

                logger.info(
    f""stats" Batch summary: {}"
        len(already_fixed_ids)} already fixed, {}
            len(still_pending_ids)} still pending")"

                # If we processed fewer than batch_size, we're done'
                if len(pending_violations) < batch_size:
                    break

            # Calculate final metrics
            processing_time = (datetime.now() - start_time).total_seconds()

            results = {
                'total_checked': total_checked,
                'already_fixed': total_already_fixed,
                'still_pending': total_still_pending,
                'files_processed': len(files_processed),
                'processing_time_seconds': processing_time,
                'cleanup_success_rate': total_already_fixed / total_checked if total_checked > 0 else 0
            }

            # Final logging
            logger.info("="*80)
            logger.info("✅ DATABASE CLEANUP COMPLETED")
            logger.info("="*80)
            logger.info(f""stats" Total Violations Checked: {total_checked}")
            logger.info(f"✅ Already Fixed: {total_already_fixed}")
            logger.info(f"⚠️ Still Pending: {total_still_pending}")
            logger.info(f"📁 Files Processed: {len(files_processed)}")
            logger.info(f"⏱️ Processing Time: {processing_time:.2f} seconds")
            logger.info(f"📈 Cleanup Rate: {results['cleanup_success_rate']:.1%}")
            logger.info("="*80)

            return results

        except Exception as e:
            logger.error(f"❌ Cleanup processing failed: {e}")
            raise


def main():
    """🔄 Main cleanup execution"""
    try:
        processor = DatabaseCleanupProcessor()

        print("\n🔄 DATABASE CLEANUP PROCESSING")
        print("="*60)
        print("🎯 Target: Update already-fixed violations in database")
        print("📋 Scope: W291 (trailing whitespace) and W293 (blank line whitespace)")

        # Execute cleanup
        results = processor.execute_cleanup(batch_size=1000)

        print("\n✅ DATABASE CLEANUP RESULTS:")
        print(f"   Total Checked: {results['total_checked']}")
        print(f"   Already Fixed: {results['already_fixed']}")
        print(f"   Still Pending: {results['still_pending']}")
        print(f"   Files Processed: {results['files_processed']}")
        print(f"   Processing Time: {results['processing_time_seconds']:.2f}s")
        print(f"   Cleanup Rate: {results['cleanup_success_rate']:.1%}")

        if results['already_fixed'] > 0:
            print(f"\n🎉 Database updated: {results['already_fixed']} violations marked as fixed!")
            print(f""stats" Actual pending violations: {results['still_pending']}")
        else:
            print("\n"stats" All checked violations are still pending and need actual fixes")

        print("\n✅ Database cleanup completed!")

    except Exception as e:
        logger.error(f"❌ Cleanup execution failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
