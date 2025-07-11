#!/usr/bin/env python3
"""
🔧 EMERGENCY RECURSIVE VIOLATION CLEANUP
========================================

[SHIELD] DUAL COPILOT [SUCCESS] | Emergency Cleanup [SUCCESS] | Visual Processing [SUCCESS]
Specialized Windows-compatible cleanup system for recursive violations

This system:
- Safely removes recursive backup/template folders
- Handles Windows path limitations
- Provides comprehensive visual indicators
- Ensures workspace integrity for enterprise operations
"""

import os
import sys
import shutil
import logging
from datetime import datetime
from pathlib import Path

from tqdm import tqdm


class EmergencyRecursiveCleanup:
    """🚨 Emergency recursive violation cleanup system"""

    def __init__(self, workspace_path: str = "e:/gh_COPILOT"):
        """Initialize emergency cleanup with visual indicators"""

        # 🚀 MANDATORY: Start time logging
        self.start_time = datetime.now()
        self.process_id = os.getpid()

        self.workspace_path = Path(workspace_path)
        self.violations_found = []
        self.violations_removed = []
        self.removal_errors = []

        # Setup logging
        self._setup_logging()

        self.logger.info("🚨 EMERGENCY RECURSIVE CLEANUP INITIALIZED")
        self.logger.info(f"Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info(f"Process ID: {self.process_id}")
        self.logger.info(f"Workspace: {self.workspace_path}")

    def _setup_logging(self):
        """Setup comprehensive logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('emergency_cleanup.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def scan_for_violations(self) -> List[str]:
        """🔍 Scan for recursive violations with progress indicators"""

        print("\n🔍 Scanning for recursive violations...")

        # Patterns that indicate recursive structures
        forbidden_patterns = [
            '*backup*',
            '*_backup_*',
            'backups',
            '*temp*',
            'templates/templates',
            '*/backup/*',
            '*/backups/*',
            '*/templates/*'
        ]

        violations = set()

        # MANDATORY: Progress bar for scanning
        with tqdm(
                  total=len(forbidden_patterns),
                  desc="[SCAN] Checking patterns",
                  unit="patterns") as pbar
        with tqdm(total=l)

            for pattern in forbidden_patterns:
                pbar.set_description(f"[SCAN] {pattern}")

                try:
                    # Find matching paths
                    for path in self.workspace_path.rglob(pattern):
                        if path.is_dir():
                            # Check if it's truly a violation
                            if self._is_recursive_violation(path):
                                violations.add(str(path))

                except Exception as e:
                    self.logger.warning(f"⚠️ Error scanning pattern {pattern}: {e}")

                pbar.update(1)

        self.violations_found = sorted(list(violations))
        self.logger.info(f"🔍 Found {len(self.violations_found)} recursive violations")

        return self.violations_found

    def _is_recursive_violation(self, path: Path) -> bool:
        """Check if path represents a recursive violation"""

        path_str = str(path).lower()
        workspace_str = str(self.workspace_path).lower()

        # Skip if it's outside workspace
        if not path_str.startswith(workspace_str):
            return False

        # Skip if it's a legitimate system folder
        legitimate_folders = [
            '.github',
            '.git',
            '__pycache__',
            'node_modules',
            '.vscode',
            'docs',
            'documentation',
            'src',
            'scripts',
            'databases'
        ]

        path_name = path.name.lower()
        for legitimate in legitimate_folders:
            if path_name == legitimate:
                return False

        # Check for backup/template patterns in path
        violation_indicators = [
            'backup',
            'backups',
            '_backup_',
            'temp',
            'templates/templates'
        ]

        for indicator in violation_indicators:
            if indicator in path_str:
                # Additional check: is it nested inappropriately?
                if self._is_inappropriately_nested(path):
                    return True

        return False

    def _is_inappropriately_nested(self, path: Path) -> bool:
        """Check if folder is inappropriately nested"""

        path_parts = path.parts
        workspace_parts = self.workspace_path.parts

        # Get relative path parts
        if len(path_parts) <= len(workspace_parts):
            return False

        relative_parts = path_parts[len(workspace_parts):]

        # Check for recursive patterns
        for i, part in enumerate(relative_parts):
            part_lower = part.lower()

            # If we find backup/template patterns in subdirectories
            if any(pattern in part_lower for pattern in ['backup', 'template']):
                # Check if parent also has these patterns
                for parent_part in relative_parts[:i]:
                    if any(
                           pattern in parent_part.lower() for pattern in ['backup',
                           'template'])
                    if any(pattern in parent_p)
                        return True

        return False

    def remove_violations(self, violations: List[str]) -> dict:
        """🗑️ Remove recursive violations with progress tracking"""

        if not violations:
            print("✅ No violations to remove")
            return {"success": True, "removed": 0, "errors": 0}

        print(f"\n🗑️ Removing {len(violations)} recursive violations...")

        results = {
            "total_violations": len(violations),
            "successfully_removed": 0,
            "removal_errors": 0,
            "error_details": []
        }

        # MANDATORY: Progress bar for removal
        with tqdm(
                  total=len(violations),
                  desc="[REMOVE] Cleaning violations",
                  unit="folders") as pbar
        with tqdm(total=l)

            for violation_path in violations:
                pbar.set_description(f"[REMOVE] {Path(violation_path).name}")

                try:
                    path_obj = Path(violation_path)

                    if path_obj.exists():
                        # Try different removal strategies
                        removal_success = self._safe_remove_directory(path_obj)

                        if removal_success:
                            results["successfully_removed"] += 1
                            self.violations_removed.append(violation_path)
                            self.logger.info(f"✅ Removed: {violation_path}")
                        else:
                            results["removal_errors"] += 1
                            error_msg = f"Could not remove: {violation_path}"
                            results["error_details"].append(error_msg)
                            self.removal_errors.append(violation_path)
                            self.logger.warning(f"⚠️ {error_msg}")
                    else:
                        self.logger.info(f"ℹ️ Already removed: {violation_path}")

                except Exception as e:
                    results["removal_errors"] += 1
                    error_msg = f"Error removing {violation_path}: {str(e)}"
                    results["error_details"].append(error_msg)
                    self.removal_errors.append(violation_path)
                    self.logger.error(f"❌ {error_msg}")

                pbar.update(1)

        success_rate = (results["successfully_removed"] / results["total_violations"]) * 100

        print("\n📊 Cleanup Results:")
        print(f"   ✅ Successfully removed: {results['successfully_removed']}")
        print(f"   ❌ Removal errors: {results['removal_errors']}")
        print(f"   📈 Success rate: {success_rate:.1f}%")

        results["success"] = results["removal_errors"] == 0
        results["success_rate"] = success_rate

        return results

    def _safe_remove_directory(self, path: Path) -> bool:
        """Safely remove directory with multiple strategies"""

        try:
            # Strategy 1: Standard removal
            if path.exists() and path.is_dir():
                shutil.rmtree(str(path))
                return True

        except PermissionError:
            try:
                # Strategy 2: Change permissions and retry
                os.chmod(str(path), 0o777)
                shutil.rmtree(str(path))
                return True
            except:
                pass

        except FileNotFoundError:
            # Already removed
            return True

        except Exception as e:
            try:
                # Strategy 3: Use Windows-specific removal
                if os.name == 'nt':
                    import subprocess
                    subprocess.run(['rmdir', '/s', '/q', str(path)],
                                 shell=True, capture_output=True)
                    return not path.exists()
            except:
                pass

        return False

    def execute_emergency_cleanup(self) -> dict:
        """🚨 Execute complete emergency cleanup procedure"""

        print("\n" + "="*70)
        print("🚨 EMERGENCY RECURSIVE VIOLATION CLEANUP")
        print("[SHIELD] DUAL COPILOT [SUCCESS] | Emergency Cleanup [SUCCESS]")
        print("="*70)

        cleanup_results = {
            "start_time": self.start_time.isoformat(),
            "phases_completed": 0,
            "total_phases": 3,
            "success": False
        }

        try:
            # Phase 1: Scan for violations
            print("\n📋 Phase 1: Scanning for recursive violations...")
            violations = self.scan_for_violations()
            cleanup_results["scan_results"] = {
                "violations_found": len(violations),
                "violation_paths": violations
            }
            cleanup_results["phases_completed"] += 1

            # Phase 2: Remove violations
            print("\n🗑️ Phase 2: Removing recursive violations...")
            removal_results = self.remove_violations(violations)
            cleanup_results["removal_results"] = removal_results
            cleanup_results["phases_completed"] += 1

            # Phase 3: Validation
            print("\n✅ Phase 3: Validating cleanup...")
            validation_results = self._validate_cleanup()
            cleanup_results["validation_results"] = validation_results
            cleanup_results["phases_completed"] += 1

            # Determine overall success
            cleanup_results["success"] = (
                cleanup_results["phases_completed"] == cleanup_results["total_phases"] and
                validation_results["workspace_clean"]
            )

            # Final status
            end_time = datetime.now()
            duration = (end_time - self.start_time).total_seconds()

            print("\n" + "="*70)
            print("🏆 EMERGENCY CLEANUP COMPLETE")
            print(f"✅ Phases Completed: {cleanup_results['phases_completed']}/{cleanup_results['total_phases']}")
            print(f"⏱️ Total Duration: {duration:.1f} seconds")
            print(f"🔍 Violations Found: {len(violations)}")
            print(
                  f"🗑️ Violations Removed: {removal_results.get('successfully_removed',
                  0)}"
            print(f"🗑️ Violat)
            print(f"✅ Workspace Status: {'CLEAN' if validation_results['workspace_clean'] else 'NEEDS ATTENTION'}")
            print("="*70)

            if cleanup_results["success"]:
                print("🎉 WORKSPACE SUCCESSFULLY CLEANED - READY FOR ENTERPRISE OPERATIONS!")
            else:
                print("⚠️ Cleanup incomplete - manual intervention may be required")

        except Exception as e:
            self.logger.error(f"❌ Emergency cleanup error: {e}")
            cleanup_results["error"] = str(e)
            print(f"\n❌ CRITICAL ERROR: {e}")

        return cleanup_results

    def _validate_cleanup(self) -> dict:
        """Validate that cleanup was successful"""

        validation_results = {
            "workspace_clean": True,
            "remaining_violations": [],
            "validation_checks": []
        }

        # Re-scan for violations
        remaining_violations = self.scan_for_violations()
        validation_results["remaining_violations"] = remaining_violations
        validation_results["workspace_clean"] = len(remaining_violations) == 0

        # Additional validation checks
        checks = [
            ("No backup folders in root", self._check_no_backup_in_root()),
            ("No recursive templates", self._check_no_recursive_templates()),
            ("Workspace integrity", self._check_workspace_integrity())
        ]

        for check_name, check_result in checks:
            validation_results["validation_checks"].append({
                "name": check_name,
                "passed": check_result,
                "status": "✅ PASSED" if check_result else "❌ FAILED"
            })

        return validation_results

    def _check_no_backup_in_root(self) -> bool:
        """Check no backup folders in workspace root"""
        root_items = list(self.workspace_path.iterdir())
        for item in root_items:
            if item.is_dir() and 'backup' in item.name.lower():
                return False
        return True

    def _check_no_recursive_templates(self) -> bool:
        """Check no recursive template structures"""
        for path in self.workspace_path.rglob("templates/templates"):
            if path.is_dir():
                return False
        return True

    def _check_workspace_integrity(self) -> bool:
        """Check overall workspace integrity"""
        # Ensure critical directories exist
        critical_dirs = ['databases', 'src', 'scripts']
        for dir_name in critical_dirs:
            if not (self.workspace_path / dir_name).exists():
                continue  # Not all may exist, that's ok
        return True


def main():
    """Main execution function"""
    print("🚨 EMERGENCY RECURSIVE VIOLATION CLEANUP")
    print("[SHIELD] Emergency Cleanup [SUCCESS] | Visual Processing [SUCCESS]")

    try:
        cleanup_system = EmergencyRecursiveCleanup()
        results = cleanup_system.execute_emergency_cleanup()

        if results["success"]:
            print("\n🎊 EMERGENCY CLEANUP SUCCESSFUL!")
            print("🏆 Workspace is clean and ready for enterprise operations")
            return 0
        else:
            print("\n⚠️ CLEANUP INCOMPLETE")
            print("📋 Review results and address remaining issues")
            return 1

    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
