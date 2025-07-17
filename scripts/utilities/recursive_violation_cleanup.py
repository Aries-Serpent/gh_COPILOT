#!/usr/bin/env python3
"""
recursive_violation_cleanup.py - Automated Recursive Folder Cleanup Script
Enterprise Standards: Flake8/PEP 8, emoji-free, visual processing indicators, anti-recursion compliance

Usage:
    python recursive_violation_cleanup.py --visual-indicators
    python recursive_violation_cleanup.py --dry-run --visual-indicators
"""
import sys
import os
import shutil
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from tqdm import tqdm
import logging

FORBIDDEN_PATTERNS = ["*backup*", "*templates*", "*temp*", "*templatetags*"]
SITE_PACKAGES_CANDIDATES = [
    Path(sys.prefix) / "Lib" / "site-packages",
    Path(sys.prefix) / "lib" / "site-packages",
]
WORKSPACE_ROOT = Path(os.getenv("GH_COPILOT_WORKSPACE", "e:/gh_COPILOT"))

TEXT_INDICATORS = {
    'start': '[START]',
    'success': '[SUCCESS]',
    'error': '[ERROR]',
    'info': '[INFO]',
    'remove': '[REMOVE]',
    'dryrun': '[DRY-RUN]',
    'scan': '[SCAN]',
    'complete': '[COMPLETE]'
}

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("recursive_cleanup")

def scan_forbidden_folders(paths, patterns):
    found = []
    for base in paths:
        if not base.exists():
            continue
        for pattern in patterns:
            for folder in base.rglob(pattern):
                if folder.is_dir():
                    found.append(folder)
    return found

def remove_folders(folders, dry_run=False):
    removed = []
    errors = []
    start_time = datetime.now()
    total = len(folders)
    with tqdm(total=total, desc="Recursive Folder Cleanup", unit="folder") as pbar:
        for folder in folders:
            try:
                if dry_run:
                    logger.info(f"{TEXT_INDICATORS['dryrun']} Would remove: {folder}")
                else:
                    shutil.rmtree(folder)
                    logger.info(f"{TEXT_INDICATORS['remove']} Removed: {folder}")
                    removed.append(str(folder))
                pbar.update(1)
                elapsed = (datetime.now() - start_time).total_seconds()
                etc = (elapsed / (pbar.n / total)) - elapsed if pbar.n > 0 else 0
                pbar.set_postfix({"Elapsed": f"{elapsed:.1f}s", "ETC": f"{etc:.1f}s"})
            except Exception as e:
                logger.error(f"{TEXT_INDICATORS['error']} Could not remove: {folder} ({e})")
                errors.append(str(folder))
                pbar.update(1)
    return removed, errors

def main():
    parser = argparse.ArgumentParser(description="Automated Recursive Folder Cleanup Script")
    parser.add_argument("--visual-indicators", action="store_true", help="Enable visual processing indicators")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be removed without deleting")
    args = parser.parse_args()

    start_time = datetime.now()
    process_id = os.getpid()
    logger.info(f"{TEXT_INDICATORS['start']} Cleanup started at {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"{TEXT_INDICATORS['info']} Process ID: {process_id}")
    logger.info(f"{TEXT_INDICATORS['info']} Workspace: {WORKSPACE_ROOT}")

    scan_paths = [WORKSPACE_ROOT] + SITE_PACKAGES_CANDIDATES
    logger.info(f"{TEXT_INDICATORS['scan']} Scanning paths: {', '.join(str(p) for p in scan_paths)}")
    folders = scan_forbidden_folders(scan_paths, FORBIDDEN_PATTERNS)
    logger.info(f"{TEXT_INDICATORS['info']} Found {len(folders)} forbidden folders.")

    if not folders:
        logger.info(f"{TEXT_INDICATORS['success']} No forbidden folders found. Anti-recursion compliance achieved.")
        logger.info(f"{TEXT_INDICATORS['complete']} Cleanup complete. You may now re-run the database optimization CLI.")
        sys.exit(0)

    removed, errors = remove_folders(folders, dry_run=args.dry_run)

    logger.info("\n--- Cleanup Summary ---")
    logger.info(f"{TEXT_INDICATORS['success']} Folders removed: {len(removed)}")
    logger.info(f"{TEXT_INDICATORS['error']} Removal errors: {len(errors)}")
    if errors:
        logger.error(f"{TEXT_INDICATORS['error']} Some violations could not be removed. Manual intervention required.")
        sys.exit(1)
    else:
        logger.info(f"{TEXT_INDICATORS['success']} All forbidden folders removed successfully.")
        logger.info(f"{TEXT_INDICATORS['complete']} Cleanup complete. You may now re-run the database optimization CLI.")
        sys.exit(0)

if __name__ == "__main__":
    main()
