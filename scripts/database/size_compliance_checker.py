#!/usr/bin/env python3
"""
Size Compliance Checker with Enterprise Logging
Fixed import-time logging configuration issue
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from tqdm import tqdm

from utils.enterprise_logging import EnterpriseLoggingManager

# SOLUTION: Import enterprise logging system
sys.path.append(str(Path(__file__).resolve().parents[2]))

# SOLUTION: Get module-specific logger without import-time configuration
logger = None  # Will be initialized when setup_logging() is called


def setup_logging() -> None:
    """🎯 Setup logging for size compliance checker"""
    global logger
    if logger is None:
        logger = EnterpriseLoggingManager.setup_module_logging(
            module_name="size_compliance_checker",
            log_file="logs/size_compliance_checker.log",
        )


def check_database_sizes(databases_dir: Path, threshold_mb: float = 99.9) -> Dict[str, float]:
    """📏 Check database sizes with enterprise logging"""
    setup_logging()

    logger.info("=" * 60)
    logger.info("📏 DATABASE SIZE COMPLIANCE CHECK")
    logger.info(f"Directory: {databases_dir}")
    logger.info(f"Threshold: {threshold_mb} MB")
    logger.info("=" * 60)

    if not databases_dir.exists():
        logger.error(f"Database directory not found: {databases_dir}")
        return {}

    db_files = list(databases_dir.glob("*.db"))
    size_results: Dict[str, float] = {}

    with tqdm(total=len(db_files), desc="📏 Checking sizes", unit="db") as pbar:
        for db_file in db_files:
            pbar.set_description(f"📏 Checking {db_file.name}")
            try:
                size_bytes = db_file.stat().st_size
                size_mb = size_bytes / (1024 * 1024)
                size_results[db_file.name] = size_mb
                if size_mb > threshold_mb:
                    logger.warning(f"⚠️ {db_file.name}: {size_mb:.2f} MB > {threshold_mb} MB")
                else:
                    logger.info(f"✅ {db_file.name}: {size_mb:.2f} MB")
            except Exception as e:
                logger.error(f"❌ Error checking {db_file.name}: {e}")
                size_results[db_file.name] = -1
            pbar.update(1)

    compliant_count = sum(1 for size in size_results.values() if 0 <= size <= threshold_mb)
    violation_count = sum(1 for size in size_results.values() if size > threshold_mb)

    logger.info("=" * 60)
    logger.info("📏 SIZE COMPLIANCE SUMMARY")
    logger.info(f"Total Databases: {len(size_results)}")
    logger.info(f"Compliant: {compliant_count}")
    logger.info(f"Violations: {violation_count}")
    if size_results:
        logger.info(f"Compliance Rate: {(compliant_count / len(size_results) * 100):.1f}%")
    logger.info("=" * 60)

    return size_results


def main() -> Dict[str, float]:
    """🎯 Main function with proper logging initialization"""
    EnterpriseLoggingManager.setup_logging(
        log_file="logs/size_compliance_main.log",
        console_output=True,
    )
    logger = EnterpriseLoggingManager.get_module_logger(__name__)
    logger.info("🚀 Size Compliance Checker Started")
    workspace_path = Path(os.getenv("GH_COPILOT_WORKSPACE", os.getcwd()))
    databases_dir = workspace_path / "databases"
    results = check_database_sizes(databases_dir)
    logger.info(f"✅ Size check complete: {len(results)} databases processed")
    return results


if __name__ == "__main__":
    main()
