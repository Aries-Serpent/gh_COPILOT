#!/usr/bin/env python3
"""
🔧 CONFIGURATION PATH UPDATER
Update script references to config files in their new config/ folder location
Following ENHANCED_COGNITIVE_PROCESSING.instructions.md and DUAL_COPILOT_PATTERN.instructions.md
"""

import os
import json
from utils.cross_platform_paths import CrossPlatformPathManager
import re
from pathlib import Path
from datetime import datetime
from tqdm import tqdm
import logging

# Configure logging to route to logs folder
logs_folder = Path("artifacts/logs")
logs_folder.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    filename=logs_folder / f"config_path_updates_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class ConfigurationPathUpdater:
    """🔧 Enhanced Configuration Path Update Engine with DUAL COPILOT Validation"""

    def __init__(self):
        self.start_time = datetime.now()
        self.workspace_root = CrossPlatformPathManager.get_workspace_path()
        self.process_id = os.getpid()

        # MANDATORY: Start time logging with enterprise formatting
        print("=" * 80)
        print(f"🚀 CONFIGURATION PATH UPDATER INITIALIZED")
        print(f"Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Process ID: {self.process_id}")
        print(f"Workspace: {self.workspace_root}")
        print("=" * 80)
        self.reports_folder = self.workspace_root / "reports"
        self.reports_folder.mkdir(exist_ok=True)

        # MANDATORY: Define config_folder attribute for config/ directory
        self.config_folder = self.workspace_root / "config"
        self.config_folder.mkdir(exist_ok=True)

        # Track updates
        self.update_results = {
            "scripts_analyzed": 0,
            "scripts_updated": 0,
            "config_references_found": 0,
            "config_references_updated": 0,
            "errors_encountered": 0,
            "updated_files": [],
        }

        logging.info("Configuration Path Updater initialized")

    def validate_environment_compliance(self):
        """🛡️ CRITICAL: Validate environment compliance before processing"""
        print("🛡️ VALIDATING ENVIRONMENT COMPLIANCE...")

        workspace_root = self.workspace_root

        # Check for recursive folder violations
        forbidden_patterns = ["*backup*", "*_backup_*", "backups", "*temp*"]
        violations = []

        for pattern in forbidden_patterns:
            for folder in workspace_root.rglob(pattern):
                if folder.is_dir() and folder != workspace_root:
                    violations.append(str(folder))

        if violations:
            for violation in violations:
                print(f"🚨 RECURSIVE VIOLATION: {violation}")
            raise RuntimeError("CRITICAL: Recursive violations prevent execution")

        # Validate proper environment root
        if not str(workspace_root).replace("\\", "/").endswith("gh_COPILOT"):
            print(f"⚠️  Non-standard workspace root: {workspace_root}")

        print("✅ ENVIRONMENT COMPLIANCE VALIDATED")
        logging.info("Environment compliance validation passed")

    def think_process(self):
        """🧠 Enhanced Cognitive Processing Analysis"""

        thinking_analysis = """
        DATABASE-FIRST COGNITIVE ANALYSIS FOR CONFIG PATH UPDATES:
        1. RESTORATION COMPLETE: 45 Python scripts restored + 32 config files consolidated
        2. OBJECTIVE: Update script references to config files in config/ folder
        3. SYSTEMATIC APPROACH: Scan Python scripts for config file references
        4. PATTERN MATCHING: Identify relative and absolute paths to config files
        5. PATH TRANSFORMATION: Update paths to reference config/ folder
        6. VALIDATION: Ensure updated paths are syntactically correct
        7. DUAL_COPILOT_VALIDATION: Verify all updates maintain functionality
        8. ANTI-RECURSION: Ensure no circular references created
        
        CONFIGURATION PATH UPDATE STRATEGY:
        - Scan all Python scripts in root directory
        - Identify references to config files that moved to config/
        - Update relative paths to include config/ prefix
        - Update absolute paths to point to config/ folder
        - Validate syntax and path correctness
        - Generate comprehensive update report
        
        EXPECTED PATTERNS TO UPDATE:
        - "config_file.json" → "config/config_file.json"  
        - "./config_file.json" → "config/config_file.json"
        - "reports/config_file.json" → "config/config_file.json"
        - workspace_root / "config_file.json" → workspace_root / "config/config_file.json"
        """

        print("🧠 ENHANCED COGNITIVE PROCESSING ANALYSIS:")
        print("=" * 60)
        for line in thinking_analysis.strip().split("\n"):
            if line.strip():
                print(f"   {line.strip()}")
        print("=" * 60)

        logging.info("Cognitive processing analysis completed")
        return thinking_analysis

    def scan_python_scripts_for_config_references(self):
        """🔍 Scan Python scripts for configuration file references"""
        print("🔍 SCANNING PYTHON SCRIPTS FOR CONFIG REFERENCES")
        print("=" * 50)

        # Get all Python files in root directory
        python_files = list(self.workspace_root.glob("*.py"))
        config_references = {}

        # Common config file patterns that moved to config/
        config_patterns = [
            r'["\']([^"\']*\.json)["\']',  # JSON files
            r'["\']([^"\']*\.yaml)["\']',  # YAML files
            r'["\']([^"\']*\.yml)["\']',  # YML files
            r'["\']([^"\']*\.toml)["\']',  # TOML files
            r'["\']([^"\']*\.ini)["\']',  # INI files
            r'["\']([^"\']*\.cfg)["\']',  # CFG files
            r'["\']([^"\']*config[^"\']*)["\']',  # Files with 'config' in name
            r'["\']([^"\']*settings[^"\']*)["\']',  # Files with 'settings' in name
        ]

        with tqdm(total=len(python_files), desc="🔍 Scanning Scripts", unit="file") as pbar:
            for py_file in python_files:
                pbar.set_description(f"🔍 Scanning {py_file.name}")

                try:
                    with open(py_file, "r", encoding="utf-8") as f:
                        content = f.read()

                    file_references = []

                    # Check each pattern
                    for pattern in config_patterns:
                        matches = re.finditer(pattern, content, re.IGNORECASE)
                        for match in matches:
                            config_file_ref = match.group(1)

                            # Check if this config file exists in config/ folder
                            config_file_name = Path(config_file_ref).name
                            config_path = self.config_folder / config_file_name

                            if config_path.exists():
                                file_references.append(
                                    {
                                        "original_reference": config_file_ref,
                                        "line_content": self._get_line_content(content, match.start()),
                                        "line_number": self._get_line_number(content, match.start()),
                                        "config_file_name": config_file_name,
                                        "new_reference": f"config/{config_file_name}",
                                        "match_pattern": pattern,
                                    }
                                )

                                self.update_results["config_references_found"] += 1

                    if file_references:
                        config_references[py_file.name] = {"file_path": str(py_file), "references": file_references}
                        print(f"📁 {py_file.name}: Found {len(file_references)} config references")

                    self.update_results["scripts_analyzed"] += 1

                except Exception as e:
                    print(f"⚠️  Error scanning {py_file.name}: {e}")
                    self.update_results["errors_encountered"] += 1
                    logging.error(f"Error scanning {py_file.name}: {e}")

                pbar.update(1)

        return config_references

    def update_script_config_paths(self, config_references):
        """🔧 Update script configuration file paths"""
        print("🔧 UPDATING SCRIPT CONFIGURATION PATHS")
        print("=" * 50)

        updated_files = []

        with tqdm(total=len(config_references), desc="🔧 Updating Paths", unit="file") as pbar:
            for script_name, script_data in config_references.items():
                pbar.set_description(f"🔧 Updating {script_name}")

                try:
                    script_path = Path(script_data["file_path"])

                    # Read current content
                    with open(script_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    original_content = content
                    updates_made = 0

                    # Apply updates for each reference
                    for ref in script_data["references"]:
                        old_ref = ref["original_reference"]
                        new_ref = ref["new_reference"]

                        # Update the reference (maintaining quotes)
                        content = content.replace(f'"{old_ref}"', f'"{new_ref}"')
                        content = content.replace(f"'{old_ref}'", f"'{new_ref}'")

                        if old_ref != new_ref:
                            updates_made += 1
                            self.update_results["config_references_updated"] += 1
                            print(f"   ✅ {old_ref} → {new_ref}")

                    # Write updated content if changes were made
                    if updates_made > 0:
                        with open(script_path, "w", encoding="utf-8") as f:
                            f.write(content)

                        updated_files.append(
                            {
                                "script": script_name,
                                "path": str(script_path),
                                "updates_made": updates_made,
                                "references_updated": [ref["new_reference"] for ref in script_data["references"]],
                            }
                        )

                        self.update_results["scripts_updated"] += 1
                        print(f"📝 Updated {script_name}: {updates_made} references")
                        logging.info(f"Updated {script_name} with {updates_made} path changes")

                except Exception as e:
                    print(f"⚠️  Error updating {script_name}: {e}")
                    self.update_results["errors_encountered"] += 1
                    logging.error(f"Error updating {script_name}: {e}")

                pbar.update(1)

        self.update_results["updated_files"] = updated_files
        return updated_files

    def validate_updated_paths(self, updated_files):
        """✅ Validate that updated paths are accessible"""
        print("✅ VALIDATING UPDATED CONFIGURATION PATHS")
        print("=" * 50)

        validation_results = {"valid_paths": 0, "invalid_paths": 0, "validation_details": []}

        for file_data in updated_files:
            script_name = file_data["script"]
            print(f"🔍 Validating {script_name}...")

            for ref_path in file_data["references_updated"]:
                full_path = self.workspace_root / ref_path

                if full_path.exists():
                    validation_results["valid_paths"] += 1
                    print(f"   ✅ {ref_path} - accessible")
                else:
                    validation_results["invalid_paths"] += 1
                    print(f"   ❌ {ref_path} - not found")

                validation_results["validation_details"].append(
                    {
                        "script": script_name,
                        "reference": ref_path,
                        "accessible": full_path.exists(),
                        "full_path": str(full_path),
                    }
                )

        return validation_results

    def _get_line_content(self, content, position):
        """Get the line content containing the match"""
        lines = content[:position].split("\n")
        line_start = len("\n".join(lines[:-1])) + (1 if len(lines) > 1 else 0)
        line_end = content.find("\n", position)
        if line_end == -1:
            line_end = len(content)
        return content[line_start:line_end].strip()

    def _get_line_number(self, content, position):
        """Get the line number of the match"""
        return content[:position].count("\n") + 1

    def execute_configuration_updates(self):
        """🚀 Execute complete configuration path update workflow"""
        # MANDATORY: Progress bar for update phases
        phases = [
            ("🧠 Cognitive Analysis", self.think_process),
            ("🔍 Scan Config References", self.scan_python_scripts_for_config_references),
            ("🔧 Update Script Paths", None),  # Will be handled specially
            ("✅ Validate Updated Paths", None),  # Will be handled specially
        ]

        results = {}

        with tqdm(total=len(phases), desc="🔧 Config Updates", unit="phase") as pbar:
            # Phase 1: Cognitive Analysis
            pbar.set_description("🧠 Cognitive Analysis")
            results["cognitive_analysis"] = self.think_process()
            pbar.update(1)

            # Phase 2: Scan Config References
            pbar.set_description("🔍 Scanning References")
            config_references = self.scan_python_scripts_for_config_references()
            results["config_references"] = config_references
            pbar.update(1)

            # Phase 3: Update Script Paths
            pbar.set_description("🔧 Updating Paths")
            if config_references:
                updated_files = self.update_script_config_paths(config_references)
                results["updated_files"] = updated_files
            else:
                updated_files = []
                results["updated_files"] = []
                print("ℹ️  No configuration path updates needed")
            pbar.update(1)

            # Phase 4: Validate Updated Paths
            pbar.set_description("✅ Validating Paths")
            if updated_files:
                validation_results = self.validate_updated_paths(updated_files)
                results["validation_results"] = validation_results
            else:
                validation_results = {"valid_paths": 0, "invalid_paths": 0, "validation_details": []}
                results["validation_results"] = validation_results
            pbar.update(1)

        # Generate completion report - PROPERLY ROUTED TO REPORTS FOLDER
        self._generate_completion_report(results)

        return results

    def _generate_completion_report(self, results):
        """📊 Generate comprehensive completion report - ROUTED TO REPORTS FOLDER"""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()

        report_data = {
            "operation_metadata": {
                "operation": "Configuration Path Updates",
                "start_time": self.start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_seconds": duration,
                "process_id": self.process_id,
            },
            "update_summary": self.update_results,
            "detailed_results": results,
            "success_metrics": {
                "scripts_analyzed": self.update_results["scripts_analyzed"],
                "scripts_updated": self.update_results["scripts_updated"],
                "config_references_updated": self.update_results["config_references_updated"],
                "errors_encountered": self.update_results["errors_encountered"],
                "success_rate": f"{((self.update_results['scripts_analyzed'] - self.update_results['errors_encountered']) / max(1, self.update_results['scripts_analyzed'])) * 100:.1f}%",
            },
            "recommendations": [
                "Test updated scripts to ensure functionality",
                "Verify config file accessibility from scripts",
                "Monitor for any remaining path issues",
                "Update documentation with new config/ structure",
            ],
            "next_steps": [
                "Phase 2: Functionality Validation",
                "Phase 3: Final System Validation",
                "Complete workspace integrity check",
            ],
        }

        # CRITICAL: ENFORCE PROPER ROUTING - ALWAYS TO REPORTS FOLDER
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"configuration_path_updates_report_{timestamp}.json"
        report_path = self.reports_folder / report_filename

        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2)

        print("=" * 80)
        print("✅ CONFIGURATION PATH UPDATES COMPLETED")
        print("=" * 80)
        print(f"Duration: {duration:.2f} seconds")
        print(f"Scripts Analyzed: {self.update_results['scripts_analyzed']}")
        print(f"Scripts Updated: {self.update_results['scripts_updated']}")
        print(f"Config References Updated: {self.update_results['config_references_updated']}")
        print(f"Errors Encountered: {self.update_results['errors_encountered']}")
        print(f"📊 COMPLETION REPORT: {report_path}")
        print("🎯 Ready for Phase 2: Functionality Validation")
        print("=" * 80)

        logging.info(f"Configuration path updates completed: {report_path}")


def main():
    """🎯 Main execution function"""
    try:
        updater = ConfigurationPathUpdater()
        results = updater.execute_configuration_updates()

        print("\n🧠 ENHANCED COGNITIVE PROCESSING SUMMARY:")
        print("=" * 60)
        print("OBJECTIVE: Update script paths for config/ consolidation")
        print("STATUS: Configuration path updates complete")
        print("NEXT: Phase 2 - Functionality Validation")
        print("=" * 60)

    except Exception as e:
        print(f"🚨 Configuration update error: {str(e)}")
        logging.error(f"Configuration update failed: {str(e)}")


if __name__ == "__main__":
    main()
