#!/usr/bin/env python3
"""
[PROCESSING] SESSION MANAGEMENT CONSOLIDATION EXECUTOR
DUAL COPILOT PATTERN: Session Management Systems Consolidation & Archival

This script consolidates all session management related scripts into a single unified system.
"""

import json
import logging
import os
import shutil
import sqlite3
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from base_consolidation_executor import BaseConsolidationExecutor

# Configure logging
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / 'session_management_consolidation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class ConsolidationResult:
    """Results from session management consolidation"""
    scripts_discovered: List[str]
    scripts_archived: List[str]
    scripts_removed: List[str]
    unified_system_verified: bool
    archive_location: str
    manifest_created: str
    timestamp: str
    summary: Dict[str, Any]


class SessionManagementConsolidationExecutor(BaseConsolidationExecutor):
    """
    [PROCESSING] SESSION MANAGEMENT CONSOLIDATION EXECUTOR

    Enterprise-compliant consolidation of session management scripts:
    - Session integrity validators
    - Session wrap-up systems
    - Graceful shutdown systems
    - Compliance certificate generators
    - Session tracking and transition systems
    """

    def __init__(self, workspace_root: str = r"e:\gh_COPILOT"):
        super().__init__(
            workspace_root=workspace_root,
            archive_root=r"E:/TEMP/gh_copilot_backup",
            group_name="session_management",
            logger=logger,
        )
        self.session_id = f"SESSION_MGMT_CONSOLIDATION_{int(time.time())}"
        self.archive_location = self.archive_dir

        # Target unified system
        self.unified_system_path = self.workspace_root / \
            "unified_session_management_system.py"

        # Session management script patterns
        self.session_management_patterns = {
            "session_integrity_validators": [
                "clean_session_integrity_validator.py",
                "comprehensive_session_integrity_validator.py"
            ],
            "session_wrap_up_systems": [
                "comprehensive_session_wrap_up.py",
                "direct_session_wrap_up.py",
                "final_session_closure.py"
            ],
            "graceful_shutdown_systems": [
                "graceful_shutdown.py"
            ],
            "compliance_generators": [
                "final_session_compliance_certificate_generator.py",
                "final_enterprise_compliance_validator.py"
            ],
            "session_tracking": [
                "session_transition_and_todo_logger.py"
            ],
            "wrap_up_orchestrators": [
                "final_conversation_wrap_up_orchestrator.py",
                "enterprise_chat_wrapup_cli.py",
                "conversation_wrap_up_generator.py"
            ]
        }

        logger.info(
            f"[LAUNCH] Session Management Consolidation Executor initialized")
        logger.info(f"Session ID: {self.session_id}")
        logger.info(f"Archive Location: {self.archive_location}")
        logger.info(f"Unified System Path: {self.unified_system_path}")

    def discover_session_management_scripts(self) -> List[str]:
        """Discover all session management related scripts in the workspace"""
        logger.info("[SEARCH] DISCOVERING SESSION MANAGEMENT SCRIPTS...")

        all_patterns: List[str] = []
        for patterns in self.session_management_patterns.values():
            all_patterns.extend(patterns)

        discovered = [str(p) for p in self.discover_files(all_patterns)]

        # Also look for PowerShell and batch files
        for ext in ['*.ps1', '*.bat']:
            discovered += [str(p) for p in self.discover_files(
                [f"**/*wrap*{ext}", f"**/*shutdown*{ext}"])]

        discovered_scripts = sorted(set(discovered))

        print(
            f"[SUCCESS] Discovered {len(discovered_scripts)} session management scripts")
        return discovered_scripts

    def create_archive_structure(self):
        """Create the archive directory structure"""
        print(
            f"\n[FOLDER] Creating archive structure at: {self.archive_location}")

        self.archive_location.mkdir(parents=True, exist_ok=True)
        self.manifest_dir.mkdir(parents=True, exist_ok=True)

    def archive_scripts(self, scripts: List[str]) -> List[str]:
        """Archive scripts to the backup location"""
        print(f"\n[ARCHIVE] Archiving {len(scripts)} scripts...")

        archived_scripts = []

        for script_path in scripts:
            try:
                script_file = Path(script_path)
                if not script_file.exists():
                    print(f"[WARNING] Script not found: {script_path}")
                    continue

                result = self.archive_files([script_file])
                if result:
                    archived_scripts.append(str(script_file))
                    print(f"[ARCHIVE] Archived {script_file.name}")
                else:
                    raise Exception("archive failed")

            except Exception as e:
                print(f"[ERROR] Failed to archive {script_path}: {e}")

        print(f"[SUCCESS] Archived {len(archived_scripts)} scripts")
        return archived_scripts

    def validate_unified_system(self) -> bool:
        """Validate that the unified session management system exists and is compliant"""
        print(f"\n[SEARCH] Validating unified session management system...")

        if not self.unified_system_path.exists():
            print(
                f"[ERROR] Unified system not found: {self.unified_system_path}")
            return False

        # Read and validate the unified system
        try:
            with open(self.unified_system_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check for required components
            required_components = [
                "DUAL COPILOT PATTERN",
                "session_integrity_validation",
                "session_wrap_up",
                "graceful_shutdown",
                "compliance_certificate",
                "anti_recursion_protection",
                "visual_processing_indicators",
                "enterprise_compliance"
            ]

            missing_components = []
            for component in required_components:
                if component.lower() not in content.lower():
                    missing_components.append(component)

            if missing_components:
                print(
                    f"[ERROR] Missing components in unified system: {missing_components}")
                return False

            print(f"[SUCCESS] Unified system validated - all components present")
            return True

        except Exception as e:
            print(f"[ERROR] Failed to validate unified system: {e}")
            return False

    def remove_legacy_scripts(self, scripts: List[str]) -> List[str]:
        """Remove legacy scripts from the workspace"""
        print(f"\n[TRASH] Removing {len(scripts)} legacy scripts...")

        removed_scripts = []

        for script_path in scripts:
            try:
                script_file = Path(script_path)
                if script_file.exists():
                    script_file.unlink()
                    removed_scripts.append(script_path)
                    print(
                        f"[TRASH] Removed: {script_file.relative_to(self.workspace_root)}")
                else:
                    print(f"[WARNING] Script already removed: {script_path}")
            except Exception as e:
                print(f"[ERROR] Failed to remove {script_path}: {e}")

        print(f"[SUCCESS] Removed {len(removed_scripts)} legacy scripts")
        return removed_scripts

    def generate_consolidation_manifest(self, result: ConsolidationResult) -> str:
        """Generate consolidation manifest"""
        print(f"\n[CLIPBOARD] Generating consolidation manifest...")

        manifest = {
            "consolidation_type": "session_management",
            "session_id": self.session_id,
            "timestamp": self.timestamp,
            "unified_system": str(self.unified_system_path),
            "archive_location": str(self.archive_location),
            "scripts_discovered": result.scripts_discovered,
            "scripts_archived": result.scripts_archived,
            "scripts_removed": result.scripts_removed,
            "summary": result.summary,
            "validation": {
                "unified_system_verified": result.unified_system_verified,
                "archive_complete": len(result.scripts_archived) == len(result.scripts_discovered),
                "removal_complete": len(result.scripts_removed) == len(result.scripts_archived)
            }
        }

        manifest_path = self.generate_manifest(manifest)
        print(f"[SUCCESS] Manifest created: {manifest_path}")
        return manifest_path

    def execute_consolidation(self) -> ConsolidationResult:
        """Execute the complete session management consolidation process"""
        print(f"\n{'='*60}")
        print(f"[PROCESSING] SESSION MANAGEMENT CONSOLIDATION")
        print(f"{'='*60}")

        # Step 1: Discover all session management scripts
        discovered_scripts = self.discover_session_management_scripts()

        # Step 2: Validate unified system exists
        unified_system_verified = self.validate_unified_system()

        # Step 3: Create archive structure
        self.create_archive_structure()

        # Step 4: Archive scripts
        archived_scripts = self.archive_scripts(discovered_scripts)

        # Step 5: Remove legacy scripts
        removed_scripts = self.remove_legacy_scripts(archived_scripts)

        # Step 6: Generate summary
        summary = {
            "total_scripts_discovered": len(discovered_scripts),
            "total_scripts_archived": len(archived_scripts),
            "total_scripts_removed": len(removed_scripts),
            "unified_system_verified": unified_system_verified,
            "categories": {}
        }

        # Categorize scripts
        for category, patterns in self.session_management_patterns.items():
            category_scripts = [s for s in discovered_scripts if any(
                pattern in Path(s).name for pattern in patterns)]
            summary["categories"][category] = len(category_scripts)

        # Create result
        result = ConsolidationResult(
            scripts_discovered=discovered_scripts,
            scripts_archived=archived_scripts,
            scripts_removed=removed_scripts,
            unified_system_verified=unified_system_verified,
            archive_location=str(self.archive_location),
            manifest_created="",
            timestamp=self.timestamp,
            summary=summary
        )

        # Step 7: Generate manifest
        manifest_path = self.generate_consolidation_manifest(result)
        result.manifest_created = manifest_path

        # Final status
        print(f"\n{'='*60}")
        print(f"[SUCCESS] SESSION MANAGEMENT CONSOLIDATION COMPLETE")
        print(f"{'='*60}")
        print(f"[CLIPBOARD] Scripts discovered: {len(discovered_scripts)}")
        print(f"[ARCHIVE] Scripts archived: {len(archived_scripts)}")
        print(f"[TRASH] Scripts removed: {len(removed_scripts)}")
        print(f"[SEARCH] Unified system verified: {unified_system_verified}")
        print(f"[FOLDER] Archive location: {self.archive_location}")
        print(f"[CLIPBOARD] Manifest created: {manifest_path}")

        return result


def main():
    """Main execution function"""
    try:
        executor = SessionManagementConsolidationExecutor()
        result = executor.execute_consolidation()

        if result.unified_system_verified and len(result.scripts_removed) > 0:
            print(
                f"\n[SUCCESS] Session Management consolidation completed successfully!")
            print(
                f"[LAUNCH] Unified system ready at: {executor.unified_system_path}")
            return 0
        else:
            print(
                f"\n[ERROR] Session Management consolidation completed with issues")
            return 1

    except Exception as e:
        logger.error(
            f"[ERROR] Critical error in session management consolidation: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
