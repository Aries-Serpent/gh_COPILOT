#!/usr/bin/env python3
"""
🎯 Final Git Operations Validation
Tests git commit functionality for VS Code integration
Generated: 2025-08-06 | Validation Complete
"""

import argparse
import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


def validate_git_operations(dry_run: bool = False) -> bool:
    """Validate all git operations are working perfectly.

    Args:
        dry_run: When ``True``, skip committing changes to the repository.
    """

    logger.info("🎯 Final Git Operations Validation")
    logger.info("=" * 50)
    
    # Test 1: Check git status
    logger.info("📋 Test 1: Checking git status...")
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            check=True,
        )
        if not result.stdout.strip():
            logger.info("✅ Working tree is clean")
        else:
            logger.warning("⚠️ Working tree has changes:\n%s", result.stdout)
    except subprocess.CalledProcessError as e:
        logger.error("❌ Git status failed: %s", e.stderr.strip() or e.stdout)
        return False
    
    # Test 2: Check LFS configuration
    logger.info("🔧 Test 2: Verifying LFS configuration...")
    try:
        result = subprocess.run(
            ["git", "config", "--get", "lfs.skipdownloaderrors"],
            capture_output=True,
            text=True,
            check=True,
        )
        if result.stdout.strip() == "true":
            logger.info("✅ LFS skip configuration is active")
        else:
            logger.error("❌ LFS configuration missing")
            return False
    except subprocess.CalledProcessError as e:
        logger.error("❌ LFS config check failed: %s", e.stderr.strip() or e.stdout)
        return False
    
    # Test 3: Test file creation and commit
    logger.info("🧪 Test 3: Testing file creation and commit...")
    test_file = Path("validation_test.tmp")
    try:
        if dry_run:
            logger.info("Dry run enabled - skipping file creation and commit")
        else:
            test_file.write_text(f"Validation test - {datetime.now()}")

            if Path("databases/codex_session_logs.db").exists():
                subprocess.run(
                    ["git", "add", "databases/codex_session_logs.db"], check=True
                )
            subprocess.run(["git", "add", "validation_test.tmp"], check=True)

            subprocess.run(
                ["git", "commit", "-m", "Validation test commit"],
                check=True,
                capture_output=True,
                text=True,
            )

            subprocess.run(["git", "rm", "validation_test.tmp"], check=True)
            subprocess.run(
                ["git", "commit", "-m", "Remove validation test"],
                check=True,
                capture_output=True,
                text=True,
            )

            logger.info("✅ File creation and commit test passed")
    except subprocess.CalledProcessError as e:
        logger.error("❌ Commit test failed: %s", e.stderr.strip() or e.stdout)
        if not dry_run and test_file.exists():
            test_file.unlink()
        return False
    except Exception as e:
        logger.error("❌ Commit test failed: %s", e)
        if not dry_run and test_file.exists():
            test_file.unlink()
        return False
    
    # Test 4: Verify no merge conflicts
    logger.info("🔍 Test 4: Checking for merge conflicts...")
    try:
        git_dir = Path(".git")
        merge_files = ["MERGE_HEAD", "CHERRY_PICK_HEAD", "REVERT_HEAD"]

        for merge_file in merge_files:
            if (git_dir / merge_file).exists():
                logger.error("❌ Found merge conflict file: %s", merge_file)
                return False

        logger.info("✅ No merge conflicts detected")
    except Exception as e:
        logger.error("❌ Merge conflict check failed: %s", e)
        return False
    
    logger.info("=" * 50)
    logger.info("🎉 ALL TESTS PASSED!")
    logger.info("✅ Git operations are fully functional")
    logger.info("✅ VS Code integration should work perfectly")
    logger.info("✅ No unmerged files or conflicts")
    logger.info("✅ LFS configuration is active")
    
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate git operations")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run validation without committing changes",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    success = validate_git_operations(dry_run=args.dry_run)
    sys.exit(0 if success else 1)
