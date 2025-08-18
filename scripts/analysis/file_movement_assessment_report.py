#!/usr/bin/env python3
"""
🔍 FILE MOVEMENT ASSESSMENT REPORT GENERATOR
Identify incorrectly moved files and create comprehensive assessment
Following ENHANCED_COGNITIVE_PROCESSING.instructions.md and PLAN_ISSUED_STATEMENT.instructions.md
"""

import os
import json
from pathlib import Path
from datetime import datetime
from tqdm import tqdm
import logging

# Configure logging to route to logs folder
logs_folder = Path("artifacts/logs")
logs_folder.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    filename=logs_folder / f"file_assessment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class FileMovementAssessment:
    """🧠 Cognitive File Movement Assessment with Enhanced Processing"""

    def __init__(self):
        self.start_time = datetime.now()
        self.workspace_root = Path(os.getcwd())

        # MANDATORY: Start time logging with enterprise formatting
        print(f"🚀 FILE MOVEMENT ASSESSMENT STARTED")
        print(f"Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Process ID: {os.getpid()}")
        print("=" * 60)

        # Define correct folder structure
        self.target_folders = {
            "logs": self.workspace_root / "artifacts" / "logs",
            "reports": self.workspace_root / "reports",
            "results": self.workspace_root / "results",
            "documentation": self.workspace_root / "documentation",
            "config": self.workspace_root / "config",
            "scripts": self.workspace_root / "scripts",
            "databases": self.workspace_root / "databases",
        }

        # Ensure reports folder exists for output
        (self.workspace_root / "reports").mkdir(exist_ok=True)

        logging.info("File Movement Assessment initialized")

    def think_process(self):
        """🧠 Enhanced Cognitive Processing - Think Function"""

        thinking_analysis = """
        DATABASE-FIRST COGNITIVE ANALYSIS:
        1. CONVERSATION REVIEW: User reported Python scripts and config files moved incorrectly again
        2. ROOT CAUSE: File categorization logic treating Python scripts as reports/logs
        3. CRITICAL ISSUE: Configuration files being moved from proper locations
        4. OBJECTIVE: Identify all incorrectly moved files and create restoration plan
        5. SYSTEMATIC_LOGIC: Separate executable scripts from data files
        6. SOLUTION_FORMULATION: Create assessment tool with proper file type recognition
        7. DUAL_COPILOT_VALIDATION: Ensure no further file misplacement
        8. ANTI-RECURSION: Validate no circular logic or redundant processing
        
        CORE PROBLEM IDENTIFIED:
        - Python executable scripts (.py) being categorized as reports/logs
        - Critical configuration files being moved from intended locations
        - Lack of proper file type validation before movement
        
        SOLUTION APPROACH:
        - Scan all target folders for misplaced Python executables
        - Identify configuration files in wrong locations
        - Create restoration plan preserving functionality
        - Implement proper file type classification
        """

        print("🧠 ENHANCED COGNITIVE PROCESSING ANALYSIS:")
        print("=" * 50)
        for line in thinking_analysis.strip().split("\n"):
            if line.strip():
                print(f"   {line.strip()}")
        print("=" * 50)

        logging.info("Cognitive processing analysis completed")
        return thinking_analysis

    def assess_python_script_misplacement(self):
        """🐍 Assess Python scripts in wrong locations"""
        print("🐍 ASSESSING PYTHON SCRIPT MISPLACEMENT")
        print("=" * 40)

        misplaced_scripts = {"in_logs": [], "in_reports": [], "in_results": [], "in_documentation": [], "in_config": []}

        # Check each target folder for Python scripts
        for folder_name, folder_path in self.target_folders.items():
            if folder_path.exists() and folder_name != "scripts":
                python_files = list(folder_path.glob("*.py"))
                if python_files:
                    print(f"⚠️  Found {len(python_files)} Python files in {folder_name}/")
                    for py_file in python_files:
                        print(f"   - {py_file.name}")
                        misplaced_scripts[f"in_{folder_name}"].append(
                            {
                                "file": py_file.name,
                                "path": str(py_file),
                                "size": py_file.stat().st_size if py_file.exists() else 0,
                                "is_executable": self._is_executable_script(py_file),
                            }
                        )

        return misplaced_scripts

    def assess_config_file_misplacement(self):
        """⚙️ Assess configuration files that should be consolidated in config/"""
        print("⚙️ ASSESSING CONFIGURATION FILE CONSOLIDATION NEEDS")
        print("=" * 40)

        config_files_scattered = {
            "in_root": [],
            "in_logs": [],
            "in_reports": [],
            "in_results": [],
            "in_documentation": [],
        }

        config_patterns = [".json", ".yaml", ".yml", ".toml", ".ini", ".cfg"]

        # Check root directory for config files (excluding critical system files)
        critical_root_files = {
            "COPILOT_NAVIGATION_MAP.json",  # Must stay in root
            "package.json",  # Must stay in root
            "pyproject.toml",  # Must stay in root
            "requirements.txt",  # Must stay in root
            "Dockerfile",  # Must stay in root
            "docker-compose.yml",  # Must stay in root
            "Makefile",  # Must stay in root
        }

        # Check root for config files that should move to config/
        for pattern in config_patterns:
            root_configs = list(self.workspace_root.glob(f"*{pattern}"))
            for config_file in root_configs:
                if (
                    config_file.name not in critical_root_files
                    and config_file.is_file()
                    and self._is_configuration_file(config_file)
                ):
                    print(f"📋 Config file in root (should move to config/): {config_file.name}")
                    config_files_scattered["in_root"].append(
                        {
                            "file": config_file.name,
                            "path": str(config_file),
                            "size": config_file.stat().st_size,
                            "type": pattern,
                            "action_needed": "move_to_config_folder",
                        }
                    )

        # Check other folders for scattered config files
        folders_to_check = ["logs", "reports", "results", "documentation"]
        for folder_name in folders_to_check:
            folder_path = self.target_folders[folder_name]
            if folder_path.exists():
                for pattern in config_patterns:
                    config_files = list(folder_path.glob(f"*{pattern}"))
                    for config_file in config_files:
                        # Check if it's actually a configuration file
                        if self._is_configuration_file(config_file):
                            print(f"⚠️  Found config file: {config_file.name} in {folder_name}/ (should be in config/)")
                            config_files_scattered[f"in_{folder_name}"].append(
                                {
                                    "file": config_file.name,
                                    "path": str(config_file),
                                    "size": config_file.stat().st_size,
                                    "type": pattern,
                                    "action_needed": "consolidate_to_config_folder",
                                }
                            )

        return config_files_scattered

    def assess_critical_files_moved(self):
        """🚨 Check for critical files that shouldn't have been moved"""
        print("🚨 ASSESSING CRITICAL FILES MOVEMENT")
        print("=" * 40)

        critical_files = [
            "COPILOT_NAVIGATION_MAP.json",
            "package.json",
            "requirements.txt",
            "pyproject.toml",
            "Dockerfile",
            "docker-compose.yml",
            "Makefile",
        ]

        critical_status = {}

        for critical_file in critical_files:
            # Check if it's in root (correct location)
            root_path = self.workspace_root / critical_file
            if root_path.exists():
                critical_status[critical_file] = "correct_location"
                print(f"✅ {critical_file} - correctly in root")
            else:
                # Search in other folders
                found_location = None
                for folder_name, folder_path in self.target_folders.items():
                    if folder_path.exists():
                        potential_path = folder_path / critical_file
                        if potential_path.exists():
                            found_location = folder_name
                            break

                if found_location:
                    critical_status[critical_file] = f"moved_to_{found_location}"
                    print(f"⚠️  {critical_file} - incorrectly moved to {found_location}/")
                else:
                    critical_status[critical_file] = "missing"
                    print(f"❌ {critical_file} - missing!")

        return critical_status

    def _is_executable_script(self, file_path):
        """Check if Python file is an executable script"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                first_lines = f.read(500)  # Read first 500 chars

            # Check for script indicators
            script_indicators = [
                'if __name__ == "__main__"',
                "def main(",
                "#!/usr/bin/env python",
                "import sys",
                "import os",
            ]

            return any(indicator in first_lines for indicator in script_indicators)

        except Exception as e:
            logging.exception("analysis script error")
            return False

    def _is_configuration_file(self, file_path):
        """Check if file is actually a configuration file"""
        config_keywords = ["config", "setting", "option", "parameter", "database", "server", "api", "env"]

        filename_lower = file_path.name.lower()
        return any(keyword in filename_lower for keyword in config_keywords)

    def generate_plan_issued_statement(self, assessment_data):
        """📋 Generate Plan Issued Statement (PIS) following framework"""
        print("📋 GENERATING PLAN ISSUED STATEMENT")
        print("=" * 40)

        pis_data = {
            "objective_definition": {
                "primary_goal": "Restore incorrectly moved files to proper locations",
                "success_criteria": "100% file functionality maintained with proper organization",
                "timeline": "Immediate correction required",
            },
            "situation_analysis": {
                "current_state": "File organization scripts moved executable Python scripts and scattered config files incorrectly",
                "misplaced_python_scripts": sum(
                    len(scripts) for scripts in assessment_data["python_misplacement"].values()
                ),
                "misplaced_config_files": sum(
                    len(configs) for configs in assessment_data["config_misplacement"].values()
                ),
                "critical_files_status": assessment_data["critical_files_status"],
                "constraints": "Must maintain all script functionality and consolidate ALL config files in config/ folder",
            },
            "database_first_analysis": {
                "production_db_status": "Available for file mapping updates",
                "pattern_matching": "Executable scripts vs data files + config consolidation required",
                "integration_readiness": "High - existing patterns available for proper classification",
            },
            "implementation_strategy": {
                "phase_1": "Identify and catalog all misplaced files",
                "phase_2": "Create restoration plan with config consolidation and script path updates",
                "phase_3": "Execute restoration with config consolidation and database updates",
                "phase_4": "Implement improved file classification logic",
            },
            "risk_assessment": {
                "high_risk": "Script functionality broken by incorrect paths",
                "medium_risk": "Configuration files scattered across multiple locations",
                "mitigation": "Update script paths for config/ consolidation, test all functionality",
            },
            "execution_plan": {
                "immediate_actions": [
                    "Stop all file movement operations",
                    "Restore Python executables to root/scripts directory",
                    "Consolidate ALL configuration files to config/ directory",
                    "Update script references to config/ paths where needed",
                    "Update database mappings",
                    "Validate all functionality",
                ],
                "validation_steps": [
                    "Test Python script execution",
                    "Verify configuration file accessibility from config/",
                    "Confirm critical file locations",
                    "Update production database mappings",
                ],
            },
        }

        return pis_data

    def execute_assessment(self):
        """🚀 Execute complete assessment workflow"""
        # MANDATORY: Progress bar for assessment phases
        phases = [
            ("🧠 Cognitive Analysis", self.think_process),
            ("🐍 Python Script Assessment", self.assess_python_script_misplacement),
            ("⚙️ Config File Assessment", self.assess_config_file_misplacement),
            ("🚨 Critical Files Check", self.assess_critical_files_moved),
        ]

        assessment_results = {}

        with tqdm(total=len(phases), desc="🔍 File Assessment", unit="phase") as pbar:
            for phase_name, phase_func in phases:
                pbar.set_description(f"{phase_name}")

                if phase_name == "🧠 Cognitive Analysis":
                    assessment_results["cognitive_analysis"] = phase_func()
                elif phase_name == "🐍 Python Script Assessment":
                    assessment_results["python_misplacement"] = phase_func()
                elif phase_name == "⚙️ Config File Assessment":
                    assessment_results["config_misplacement"] = phase_func()
                elif phase_name == "🚨 Critical Files Check":
                    assessment_results["critical_files_status"] = phase_func()

                pbar.update(1)

        # Generate PIS
        pis_data = self.generate_plan_issued_statement(assessment_results)
        assessment_results["plan_issued_statement"] = pis_data

        # Generate final report - PROPERLY ROUTED TO REPORTS FOLDER
        self._generate_assessment_report(assessment_results)

        return assessment_results

    def _generate_assessment_report(self, assessment_results):
        """📊 Generate comprehensive assessment report - ROUTED TO REPORTS FOLDER"""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()

        report_data = {
            "assessment_metadata": {
                "operation": "File Movement Assessment",
                "start_time": self.start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_seconds": duration,
                "assessment_type": "Post-Movement Validation",
            },
            "assessment_results": assessment_results,
            "recommendations": [
                "Immediately restore misplaced Python executable scripts",
                "Restore configuration files to proper accessible locations",
                "Update file classification logic to distinguish executables from data",
                "Implement validation before any file movements",
                "Update production database with corrected file mappings",
            ],
            "next_steps": [
                "User approval of Plan Issued Statement",
                "Execute file restoration plan",
                "Validate all script functionality",
                "Update database mappings",
                "Implement improved file classification",
            ],
        }

        # CRITICAL: ENFORCE PROPER ROUTING - ALWAYS TO REPORTS FOLDER
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"file_movement_assessment_report_{timestamp}.json"
        report_path = self.workspace_root / "reports" / report_filename

        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2)

        print("=" * 60)
        print("✅ FILE MOVEMENT ASSESSMENT COMPLETED")
        print("=" * 60)
        print(f"Duration: {duration:.2f} seconds")
        print(f"📊 ASSESSMENT REPORT: {report_path}")
        print("📋 Plan Issued Statement generated for review")
        print("⚠️  Awaiting user approval before proceeding with corrections")
        print("=" * 60)

        logging.info(f"Assessment report generated: {report_path}")


def main():
    """🎯 Main execution function"""
    try:
        assessor = FileMovementAssessment()
        assessor.execute_assessment()

        print("\n🧠 ENHANCED COGNITIVE PROCESSING SUMMARY:")
        print("=" * 50)
        print("OBJECTIVE: Identify and correct file movement errors")
        print("STATUS: Assessment complete, awaiting user approval")
        print("NEXT: Review Plan Issued Statement and approve corrections")
        print("=" * 50)

    except Exception as e:
        logging.exception("analysis script error")
        print(f"🚨 Assessment error: {str(e)}")
        logging.exception("Assessment failed")
        raise


if __name__ == "__main__":
    main()
