#!/usr/bin/env python3
"""
🚨 DISASTER RECOVERY CONSOLIDATION EXECUTOR
==========================================
Archives individual disaster recovery scripts and validates unified system

🎯 DUAL COPILOT PATTERN: Primary Consolidator + Secondary Validator
🎬 Visual Processing Indicators: MANDATORY
🛡️ Anti-Recursion Protection: ENABLED
📦 External Archive Location: E:/TEMP/gh_copilot_backup

Version: 1.0.0
Created: July 7, 2025
Target: Complete disaster recovery script consolidation
"""

import hashlib
import logging
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from tqdm import tqdm

from base_consolidation_executor import BaseConsolidationExecutor

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)


# Configure enterprise logging
logging.basicConfig(]
    format = '%(asctime)s - %(levelname)s - %(message)s',
    handlers = [
            LOG_DIR / 'disaster_recovery_consolidation.log', encoding= 'utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


@ dataclass
class ConsolidationResult:
    """Consolidation operation result"""
    source_path: str
    archive_path: str
    file_size: int
    file_hash: str
    consolidation_status: str = "PENDING"
    error_message: str = ""


class DisasterRecoveryConsolidator(BaseConsolidationExecutor):
    """🚨 Disaster recovery script consolidation system"""

    def __init__(self):
        self.start_time = datetime.now()
        super().__init__(]
        )
        self.consolidation_timestamp = self.timestamp
        self.external_archive_root = self.archive_root

        self.consolidation_results = {
            "consolidation_timestamp": self.start_time.isoformat(),
            "workspace_root": str(self.workspace_root),
            "external_archive_root": str(self.external_archive_root),
            "scripts_found": 0,
            "scripts_archived": 0,
            "scripts_failed": 0,
            "total_size_archived": 0,
            "consolidated_files": [],
            "validation_results": {}
        }

        # Visual indicators
        self.visual_indicators = {
        }

        logger.info("🚨 DISASTER RECOVERY CONSOLIDATION EXECUTOR INITIALIZED")
        logger.info(f"Workspace: {self.workspace_root}")
        logger.info(f"External Archive: {self.external_archive_root}")
        logger.info(f"Timestamp: {self.consolidation_timestamp}")
        print("=" * 60)

    def discover_disaster_recovery_scripts(self) -> List[str]:
        """🔍 Discover all disaster recovery scripts for consolidation"""
        logger.info("🔍 DISCOVERING DISASTER RECOVERY SCRIPTS...")

        script_patterns = [
        ]

        print("🔍 Scanning for disaster recovery scripts...")
        discovered = self.discover_files(]
            script_patterns, ["unified_disaster_recovery_system.py"])
        for path in discovered:
            logger.info(f"📄 Found: {path.relative_to(self.workspace_root)}")

        self.consolidation_results["scripts_found"] = len(discovered)
        logger.info(
                    len(discovered))

        return [str(p) for p in discovered]

    def create_archive_structure(self):
        """📁 Create archive directory structure"""
        logger.info("📁 CREATING ARCHIVE STRUCTURE...")

        archive_directories = [
        ]

        for directory in archive_directories:
            try:
                directory.mkdir(parents=True, exist_ok=True)
                logger.info(f"✅ Created: {directory}")
            except Exception as e:
                logger.error(f"❌ Failed to create {directory}: {e}")
                raise

    def archive_disaster_recovery_scripts(]
            self, scripts: List[str]) -> Dict[str, Any]:
        """📦 Archive disaster recovery scripts to external location"""
        logger.info("📦 ARCHIVING DISASTER RECOVERY SCRIPTS...")

        archived_count = 0
        total_size = 0

        print("📦 Archiving disaster recovery scripts...")
        with tqdm(total=len(scripts), desc="Archive Progress", unit="script") as pbar:
            for script_path in scripts:
                pbar.set_description(f"Archiving: {Path(script_path).name}")
                src = Path(script_path)
                result = self.archive_files([src])
                if result:
                    _, target_path = result[0]
                    file_size = src.stat().st_size
                    file_hash = self.calculate_file_hash(src)
                    self.consolidation_results["consolidated_files"].append(]
                                source_path=str(src),
                                archive_path=str(target_path),
                                file_size=file_size,
                                file_hash=file_hash,
                                consolidation_status="SUCCESS")
                        )
                    )
                    archived_count += 1
                    total_size += file_size
                    src.unlink()
                else:
                    self.consolidation_results["consolidated_files"].append(]
                                source_path=str(src),
                                archive_path="",
                                file_size=0,
                                file_hash="",
                                consolidation_status="FAILED",
                                error_message="archive failed")
                        )
                    )
                pbar.update(1)

        failed_count = len(scripts) - archived_count
        self.consolidation_results["scripts_archived"] = archived_count
        self.consolidation_results["scripts_failed"] = failed_count
        self.consolidation_results["total_size_archived"] = total_size

        logger.info("📊 Consolidation Summary:")
        logger.info("  ✅ Successfully archived: %s", archived_count)
        logger.info("  ❌ Failed: %s", failed_count)
        logger.info("  📦 Total size: %.2f KB", total_size / 1024)

        return self.consolidation_results

    def validate_unified_system(self) -> Dict[str, Any]:
        """🎯 Validate unified disaster recovery system"""
        logger.info("🎯 VALIDATING UNIFIED DISASTER RECOVERY SYSTEM...")

        validation_results = {
        }

        print("🎯 Validating unified system...")

        # Check if unified system exists
        unified_system_path = self.workspace_root / \
            "unified_disaster_recovery_system.py"
        if unified_system_path.exists():
            validation_results["unified_system_exists"] = True
            logger.info("✅ Unified disaster recovery system exists")

            # Basic functionality test
            try:
                # Read and verify basic structure
                with open(unified_system_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                required_components = [
                ]

                if all(component in content for component in required_components):
                    validation_results["unified_system_functional"] = True
                    logger.info(
                        "✅ Unified system functional components verified")
                else:
                    logger.warning("⚠️ Some unified system components missing")

            except Exception as e:
                logger.error(f"❌ Error validating unified system: {e}")
        else:
            logger.error("❌ Unified disaster recovery system not found")

        # Check if legacy scripts are removed
        remaining_scripts = self.discover_disaster_recovery_scripts()
        if len(remaining_scripts) == 0:
            validation_results["legacy_scripts_removed"] = True
            logger.info("✅ All legacy disaster recovery scripts removed")
        else:
            logger.warning(
                f"⚠️ {len(remaining_scripts)} legacy scripts still present")

        # Check archive integrity
        archive_base = self.external_archive_root / "consolidated_scripts" / \
            "disaster_recovery" / self.consolidation_timestamp
        if archive_base.exists():
            archived_files = list(archive_base.glob("**/*.py"))
            if len(archived_files) > 0:
                validation_results["archive_integrity"] = True
                logger.info(
                    f"✅ Archive integrity verified: {len(archived_files)} files")
            else:
                logger.warning("⚠️ No archived files found")
        else:
            logger.error("❌ Archive directory not found")

        # Overall consolidation status
        validation_results["consolidation_complete"] = all(]
            validation_results["unified_system_exists"],
            validation_results["unified_system_functional"],
            validation_results["legacy_scripts_removed"],
            validation_results["archive_integrity"]
        ])

        self.consolidation_results["validation_results"] = validation_results

        if validation_results["consolidation_complete"]:
            logger.info("✅ DISASTER RECOVERY CONSOLIDATION: COMPLETE")
        else:
            logger.warning("⚠️ DISASTER RECOVERY CONSOLIDATION: INCOMPLETE")

        return validation_results

    def calculate_file_hash(self, file_path: Path) -> str:
        """🔐 Calculate SHA256 hash of file"""
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception:
            return "HASH_ERROR"

    def generate_consolidation_manifest(self):
        """📋 Generate consolidation manifest"""
        logger.info("📋 GENERATING CONSOLIDATION MANIFEST...")

        manifest_data = {
                "source_workspace": str(self.workspace_root),
                "archive_location": str(self.external_archive_root)},
            "summary": {]
                "scripts_found": self.consolidation_results["scripts_found"],
                "scripts_archived": self.consolidation_results["scripts_archived"],
                "scripts_failed": self.consolidation_results["scripts_failed"],
                "total_size_kb": self.consolidation_results["total_size_archived"] / 1024
            },
            "file_details": self.consolidation_results["consolidated_files"],
            "validation_results": self.consolidation_results.get("validation_results", {}),
            "consolidation_complete": self.consolidation_results.get("validation_results", {}).get("consolidation_complete", False)
        }

        return self.generate_manifest(manifest_data)

    def execute_disaster_recovery_consolidation(self) -> Dict[str, Any]:
        """🚀 Execute complete disaster recovery consolidation"""
        logger.info("🚀 EXECUTING DISASTER RECOVERY CONSOLIDATION...")

        consolidation_phases = [
            ("🔍 Script Discovery", self.discover_disaster_recovery_scripts, 20),
            ("📁 Archive Structure", self.create_archive_structure, 10),
            ("📦 Script Archival", None, 40),  # Special handling
            ("🎯 System Validation", self.validate_unified_system, 20),
            ("📋 Manifest Generation", self.generate_consolidation_manifest, 10)
        ]

        print("🚀 Starting disaster recovery consolidation...")
        with tqdm(total=100, desc="🚨 DR Consolidation", unit="%") as pbar:

            # Phase 1: Script Discovery
            pbar.set_description("🔍 Script Discovery")
            discovered_scripts = consolidation_phases[0][1]()
            pbar.update(20)

            if not discovered_scripts:
                logger.info(
                    "ℹ️ No disaster recovery scripts found to consolidate")
                pbar.update(80)  # Skip remaining phases
            else:
                # Phase 2: Archive Structure
                pbar.set_description("📁 Archive Structure")
                consolidation_phases[1][1]()
                pbar.update(10)

                # Phase 3: Script Archival
                pbar.set_description("📦 Script Archival")
                self.archive_disaster_recovery_scripts(discovered_scripts)
                pbar.update(40)

                # Phase 4: System Validation
                pbar.set_description("🎯 System Validation")
                consolidation_phases[3][1]()
                pbar.update(20)

                # Phase 5: Manifest Generation
                pbar.set_description("📋 Manifest Generation")
                manifest_path = consolidation_phases[4][1]()
                pbar.update(10)

        # Calculate duration
        duration = datetime.now() - self.start_time

        logger.info("✅ DISASTER RECOVERY CONSOLIDATION COMPLETED")
        logger.info(f"Duration: {duration}")
        logger.info(
            f"Scripts Consolidated: {self.consolidation_results['scripts_archived']}")

        return {]
            "duration": str(duration),
            "summary": self.consolidation_results
        }


def main():
    """🚀 Main consolidation execution"""
    print("🚨 DISASTER RECOVERY CONSOLIDATION EXECUTOR")
    print("=" * 50)
    print("Target: Consolidate individual scripts into unified system")
    print("Archive: E:/TEMP/gh_copilot_backup")
    print("=" * 50)

    # Initialize consolidator
    consolidator = DisasterRecoveryConsolidator()

    # Execute consolidation
    result = consolidator.execute_disaster_recovery_consolidation()

    print("\n" + "=" * 60)
    print("🎯 DISASTER RECOVERY CONSOLIDATION SUMMARY")
    print("=" * 60)
    print(f"Status: {result['status']}")
    print(f"Duration: {result['duration']}")

    if result['status'] == 'SUCCESS':
        summary = result['summary']
        print(f"Scripts Found: {summary['scripts_found']}")
        print(f"Scripts Archived: {summary['scripts_archived']}")
        print(f"Scripts Failed: {summary['scripts_failed']}")
        print(f"Total Size: {summary['total_size_archived'] / 1024:.2f} KB")

        validation = summary.get('validation_results', {})
        print(
            f"Consolidation Complete: {validation.get('consolidation_complete', False)}")

    print("=" * 60)
    print("🎯 DISASTER RECOVERY CONSOLIDATION COMPLETE!")

    return result


if __name__ == "__main__":
    try:
        result = main()
        sys.exit(0 if result['status'] == 'SUCCESS' else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Consolidation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Consolidation failed: {e}")
        sys.exit(1)
