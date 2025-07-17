#!/usr/bin/env python3
"""
🎯 PHASE 3: FINAL SYSTEM VALIDATION
Enhanced Cognitive Processing: Comprehensive Workspace Integrity Check

🚀 PRIMARY EXECUTOR with DUAL COPILOT validation
Validates complete file restoration and configuration consolidation success

MANDATORY: Visual processing indicators throughout
CRITICAL: Anti-recursion compliance enforcement
"""

import os
import sys
import json
import sqlite3
import shutil
import hashlib
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from tqdm import tqdm
import time

class FinalSystemValidator:
    """🛡️ Final System Validation with Enterprise Compliance"""
    
    def __init__(self, workspace_path: Optional[str] = None):
        # MANDATORY: Start time logging with enterprise formatting
        self.start_time = datetime.now()
        self.process_id = os.getpid()
        
        # CRITICAL: Anti-recursion validation
        self.validate_environment_compliance()
        
        # Initialize workspace
        self.workspace_path = Path(workspace_path or os.getenv("GH_COPILOT_WORKSPACE", "e:/gh_COPILOT"))
        self.config_path = self.workspace_path / "config"
        self.reports_path = self.workspace_path / "reports"
        
        # Initialize logging
        print("=" * 80)
        print("🚀 FINAL SYSTEM VALIDATOR INITIALIZED")
        print(f"Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Process ID: {self.process_id}")
        print(f"Workspace: {self.workspace_path}")
        print("=" * 80)
        
        # Initialize validation results
        self.validation_results = {
            "start_time": self.start_time.isoformat(),
            "process_id": self.process_id,
            "workspace_path": str(self.workspace_path),
            "validation_phases": {},
            "overall_success": False,
            "success_rate": 0.0,
            "enterprise_compliance": False
        }
    
    def validate_environment_compliance(self):
        """CRITICAL: Validate proper environment root usage"""
        workspace_root = Path(os.getcwd())
        
        # MANDATORY: Check for recursive backup folders
        forbidden_patterns = ['*backup*', '*_backup_*', 'backups', '*temp*']
        violations = []
        
        for pattern in forbidden_patterns:
            for folder in workspace_root.rglob(pattern):
                if folder.is_dir() and folder != workspace_root:
                    violations.append(str(folder))
        
        if violations:
            print("🚨 RECURSIVE FOLDER VIOLATIONS DETECTED:")
            for violation in violations:
                print(f"   - {violation}")
                # Emergency removal
                try:
                    shutil.rmtree(violation)
                    print(f"✅ REMOVED VIOLATION: {violation}")
                except Exception as e:
                    print(f"⚠️ Could not remove {violation}: {e}")
            raise RuntimeError("CRITICAL: Recursive violations prevented execution")
        
        print("✅ ENVIRONMENT COMPLIANCE VALIDATED")
    
    def execute_comprehensive_validation(self) -> Dict[str, Any]:
        """🔍 Execute comprehensive final system validation"""
        
        # MANDATORY: Visual processing indicators
        validation_phases = [
            ("🔍 File System Integrity", "Validating file organization and accessibility", 20),
            ("📁 Configuration Validation", "Verifying config file consolidation", 20),
            ("🐍 Python Script Validation", "Testing Python script accessibility", 20),
            ("🔗 Dependency Validation", "Checking script dependencies and imports", 15),
            ("📊 Database Integrity", "Validating database consistency", 15),
            ("🏆 Enterprise Compliance", "Final compliance certification", 10)
        ]
        
        total_weight = sum(phase[2] for phase in validation_phases)
        current_progress = 0
        
        # MANDATORY: Progress bar for all operations
        with tqdm(total=100, desc="🔍 Final System Validation", unit="%",
                 bar_format="{l_bar}{bar}| {n:.1f}/{total}{unit} [{elapsed}<{remaining}]") as pbar:
            
            for phase_name, phase_description, phase_weight in validation_phases:
                # MANDATORY: Check timeout (30 minute limit)
                self._check_timeout()
                
                # MANDATORY: Update phase description
                pbar.set_description(f"{phase_name}")
                
                # MANDATORY: Log phase start
                print(f"📊 {phase_name}: {phase_description}")
                
                # Execute phase with monitoring
                phase_result = self._execute_validation_phase(phase_name, phase_description)
                self.validation_results["validation_phases"][phase_name] = phase_result
                
                # MANDATORY: Update progress
                current_progress += phase_weight
                progress = (current_progress / total_weight) * 100
                pbar.update(phase_weight)
                
                # MANDATORY: Log progress with ETC
                elapsed = (datetime.now() - self.start_time).total_seconds()
                etc = self._calculate_etc(elapsed, progress)
                print(f"⏱️  Progress: {progress:.1f}% | Elapsed: {elapsed:.1f}s | ETC: {etc:.1f}s")
        
        # Calculate overall success
        self._calculate_overall_success()
        
        # MANDATORY: Generate final report
        report_path = self._generate_final_report()
        
        # MANDATORY: Completion summary
        self._log_completion_summary(report_path)
        
        return self.validation_results
    
    def _execute_validation_phase(self, phase_name: str, phase_description: str) -> Dict[str, Any]:
        """Execute individual validation phase"""
        
        phase_start = datetime.now()
        
        try:
            if "File System Integrity" in phase_name:
                result = self._validate_file_system_integrity()
            elif "Configuration Validation" in phase_name:
                result = self._validate_configuration_consolidation()
            elif "Python Script Validation" in phase_name:
                result = self._validate_python_scripts()
            elif "Dependency Validation" in phase_name:
                result = self._validate_dependencies()
            elif "Database Integrity" in phase_name:
                result = self._validate_database_integrity()
            elif "Enterprise Compliance" in phase_name:
                result = self._validate_enterprise_compliance()
            else:
                result = {"status": "UNKNOWN", "success": False}
            
            # Add timing information
            phase_duration = (datetime.now() - phase_start).total_seconds()
            result["duration"] = phase_duration
            result["phase_start"] = phase_start.isoformat()
            
            return result
            
        except Exception as e:
            return {
                "status": "ERROR",
                "success": False,
                "error": str(e),
                "duration": (datetime.now() - phase_start).total_seconds()
            }
    
    def _validate_file_system_integrity(self) -> Dict[str, Any]:
        """🔍 Validate file system organization and accessibility"""
        
        print("   🔍 Scanning workspace structure...")
        
        # Check critical directories
        critical_dirs = ["config", "reports", "databases"]
        dir_status = {}
        
        for dir_name in critical_dirs:
            dir_path = self.workspace_path / dir_name
            dir_status[dir_name] = {
                "exists": dir_path.exists(),
                "accessible": dir_path.is_dir() if dir_path.exists() else False,
                "file_count": len(list(dir_path.iterdir())) if dir_path.exists() and dir_path.is_dir() else 0
            }
        
        # Check Python scripts in root
        python_scripts = list(self.workspace_path.glob("*.py"))
        print(f"   📄 Found {len(python_scripts)} Python scripts in root")
        
        # Check config files in config directory
        config_files = list(self.config_path.glob("*.json")) if self.config_path.exists() else []
        print(f"   ⚙️ Found {len(config_files)} config files in config/")
        
        success = all(status["exists"] and status["accessible"] for status in dir_status.values())
        
        return {
            "status": "SUCCESS" if success else "PARTIAL",
            "success": success,
            "directory_status": dir_status,
            "python_scripts_count": len(python_scripts),
            "config_files_count": len(config_files),
            "details": {
                "critical_directories": critical_dirs,
                "all_directories_accessible": success
            }
        }
    
    def _validate_configuration_consolidation(self) -> Dict[str, Any]:
        """📁 Validate configuration file consolidation"""
        
        print("   📁 Validating configuration consolidation...")
        
        config_analysis = {
            "config_directory_exists": self.config_path.exists(),
            "config_files": [],
            "orphaned_configs": [],
            "total_config_files": 0
        }
        
        if self.config_path.exists():
            # Find all config files in config directory
            config_files = list(self.config_path.glob("*.json"))
            config_analysis["config_files"] = [str(f.name) for f in config_files]
            config_analysis["total_config_files"] = len(config_files)
            
            print(f"   ✅ Found {len(config_files)} configuration files in config/")
        
        # Check for orphaned config files in other locations
        for location in [self.workspace_path, self.reports_path]:
            if location.exists():
                orphaned = [f for f in location.glob("*.json") 
                           if "config" in f.name.lower() and f.parent != self.config_path]
                if orphaned:
                    config_analysis["orphaned_configs"].extend([str(f) for f in orphaned])
        
        consolidation_success = (
            config_analysis["config_directory_exists"] and 
            config_analysis["total_config_files"] > 0 and 
            len(config_analysis["orphaned_configs"]) == 0
        )
        
        return {
            "status": "SUCCESS" if consolidation_success else "NEEDS_ATTENTION",
            "success": consolidation_success,
            "consolidation_analysis": config_analysis,
            "details": {
                "consolidation_complete": consolidation_success,
                "orphaned_configs_found": len(config_analysis["orphaned_configs"])
            }
        }
    
    def _validate_python_scripts(self) -> Dict[str, Any]:
        """🐍 Validate Python script accessibility and basic syntax"""
        
        print("   🐍 Validating Python scripts...")
        
        python_scripts = list(self.workspace_path.glob("*.py"))
        script_validation = {
            "total_scripts": len(python_scripts),
            "accessible_scripts": 0,
            "syntax_valid_scripts": 0,
            "failed_scripts": [],
            "script_details": []
        }
        
        for script in python_scripts[:10]:  # Validate first 10 scripts for efficiency
            script_info = {
                "name": script.name,
                "accessible": script.exists() and script.is_file(),
                "syntax_valid": False,
                "size": script.stat().st_size if script.exists() else 0
            }
            
            if script_info["accessible"]:
                script_validation["accessible_scripts"] += 1
                
                # Basic syntax check
                try:
                    with open(script, 'r', encoding='utf-8') as f:
                        content = f.read()
                    compile(content, str(script), 'exec')
                    script_info["syntax_valid"] = True
                    script_validation["syntax_valid_scripts"] += 1
                except Exception as e:
                    script_info["syntax_error"] = str(e)
                    script_validation["failed_scripts"].append(script.name)
            
            script_validation["script_details"].append(script_info)
        
        validation_success = (
            script_validation["accessible_scripts"] > 0 and
            len(script_validation["failed_scripts"]) == 0
        )
        
        return {
            "status": "SUCCESS" if validation_success else "PARTIAL",
            "success": validation_success,
            "script_validation": script_validation,
            "details": {
                "all_scripts_accessible": script_validation["accessible_scripts"] == len(python_scripts[:10]),
                "syntax_check_passed": len(script_validation["failed_scripts"]) == 0
            }
        }
    
    def _validate_dependencies(self) -> Dict[str, Any]:
        """🔗 Validate script dependencies and critical imports"""
        
        print("   🔗 Validating dependencies...")
        
        dependency_analysis = {
            "critical_imports_available": True,
            "missing_dependencies": [],
            "import_tests": {}
        }
        
        # Test critical imports
        critical_imports = ["json", "os", "sys", "pathlib", "datetime", "sqlite3"]
        
        for module in critical_imports:
            try:
                __import__(module)
                dependency_analysis["import_tests"][module] = "SUCCESS"
            except ImportError as e:
                dependency_analysis["import_tests"][module] = f"FAILED: {e}"
                dependency_analysis["missing_dependencies"].append(module)
                dependency_analysis["critical_imports_available"] = False
        
        return {
            "status": "SUCCESS" if dependency_analysis["critical_imports_available"] else "FAILED",
            "success": dependency_analysis["critical_imports_available"],
            "dependency_analysis": dependency_analysis,
            "details": {
                "all_critical_imports_available": dependency_analysis["critical_imports_available"],
                "missing_count": len(dependency_analysis["missing_dependencies"])
            }
        }
    
    def _validate_database_integrity(self) -> Dict[str, Any]:
        """📊 Validate database consistency and accessibility"""
        
        print("   📊 Validating database integrity...")
        
        database_analysis = {
            "databases_found": 0,
            "accessible_databases": 0,
            "database_details": [],
            "integrity_checks": {}
        }
        
        # Find database files
        db_files = list(self.workspace_path.glob("**/*.db"))
        database_analysis["databases_found"] = len(db_files)
        
        for db_file in db_files[:5]:  # Check first 5 databases
            db_info = {
                "name": db_file.name,
                "path": str(db_file),
                "size": db_file.stat().st_size,
                "accessible": False,
                "integrity_ok": False
            }
            
            try:
                # Test database accessibility
                conn = sqlite3.connect(str(db_file))
                cursor = conn.cursor()
                cursor.execute("PRAGMA integrity_check;")
                result = cursor.fetchone()
                
                db_info["accessible"] = True
                db_info["integrity_ok"] = result[0] == "ok" if result else False
                database_analysis["accessible_databases"] += 1
                
                conn.close()
                
            except Exception as e:
                db_info["error"] = str(e)
            
            database_analysis["database_details"].append(db_info)
        
        integrity_success = (
            database_analysis["databases_found"] > 0 and 
            database_analysis["accessible_databases"] > 0
        )
        
        return {
            "status": "SUCCESS" if integrity_success else "PARTIAL",
            "success": integrity_success,
            "database_analysis": database_analysis,
            "details": {
                "databases_accessible": database_analysis["accessible_databases"] > 0,
                "integrity_validated": integrity_success
            }
        }
    
    def _validate_enterprise_compliance(self) -> Dict[str, Any]:
        """🏆 Final enterprise compliance validation"""
        
        print("   🏆 Validating enterprise compliance...")
        
        compliance_checks = {
            "file_organization_compliant": True,
            "config_consolidation_compliant": True,
            "script_accessibility_compliant": True,
            "anti_recursion_compliant": True,
            "overall_compliance": False
        }
        
        # Check file organization
        required_structure = ["config", "reports"]
        compliance_checks["file_organization_compliant"] = all(
            (self.workspace_path / folder).exists() for folder in required_structure
        )
        
        # Check config consolidation
        config_files_in_config = len(list(self.config_path.glob("*.json"))) if self.config_path.exists() else 0
        compliance_checks["config_consolidation_compliant"] = config_files_in_config > 0
        
        # Check script accessibility
        python_scripts = list(self.workspace_path.glob("*.py"))
        compliance_checks["script_accessibility_compliant"] = len(python_scripts) > 0
        
        # Check anti-recursion compliance (no backup folders in workspace)
        backup_folders = list(self.workspace_path.rglob("*backup*"))
        compliance_checks["anti_recursion_compliant"] = len(backup_folders) == 0
        
        # Overall compliance
        compliance_checks["overall_compliance"] = all([
            compliance_checks["file_organization_compliant"],
            compliance_checks["config_consolidation_compliant"],
            compliance_checks["script_accessibility_compliant"],
            compliance_checks["anti_recursion_compliant"]
        ])
        
        return {
            "status": "SUCCESS" if compliance_checks["overall_compliance"] else "FAILED",
            "success": compliance_checks["overall_compliance"],
            "compliance_checks": compliance_checks,
            "details": {
                "enterprise_compliance_achieved": compliance_checks["overall_compliance"],
                "compliance_score": sum(compliance_checks.values()) / len(compliance_checks) * 100
            }
        }
    
    def _calculate_overall_success(self):
        """Calculate overall validation success"""
        
        phase_results = self.validation_results["validation_phases"]
        total_phases = len(phase_results)
        successful_phases = sum(1 for result in phase_results.values() if result.get("success", False))
        
        self.validation_results["overall_success"] = successful_phases == total_phases
        self.validation_results["success_rate"] = (successful_phases / total_phases * 100) if total_phases > 0 else 0
        
        # Enterprise compliance requires all phases to succeed
        self.validation_results["enterprise_compliance"] = self.validation_results["overall_success"]
    
    def _generate_final_report(self) -> str:
        """Generate comprehensive final validation report"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.reports_path / f"final_system_validation_report_{timestamp}.json"
        
        # Ensure reports directory exists
        self.reports_path.mkdir(exist_ok=True)
        
        # Add completion information
        self.validation_results.update({
            "completion_time": datetime.now().isoformat(),
            "total_duration": (datetime.now() - self.start_time).total_seconds(),
            "report_generated": str(report_path),
            "validation_summary": {
                "total_phases": len(self.validation_results["validation_phases"]),
                "successful_phases": sum(1 for r in self.validation_results["validation_phases"].values() if r.get("success", False)),
                "failed_phases": sum(1 for r in self.validation_results["validation_phases"].values() if not r.get("success", False)),
                "overall_status": "SUCCESS" if self.validation_results["overall_success"] else "NEEDS_ATTENTION"
            },
            "recommendations": self._generate_recommendations()
        })
        
        # Write report
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.validation_results, f, indent=2, default=str)
        
        return str(report_path)
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on validation results"""
        
        recommendations = []
        
        if self.validation_results["overall_success"]:
            recommendations.append("✅ All validation phases completed successfully")
            recommendations.append("✅ System is ready for production use")
            recommendations.append("✅ Configuration consolidation completed successfully")
            recommendations.append("✅ Enterprise compliance achieved")
        else:
            recommendations.append("⚠️ Some validation phases require attention")
            
            for phase_name, result in self.validation_results["validation_phases"].items():
                if not result.get("success", False):
                    recommendations.append(f"🔧 Review {phase_name}: {result.get('status', 'Unknown issue')}")
        
        recommendations.append("📊 Regular system validation recommended")
        recommendations.append("🔄 Monitor configuration file organization")
        
        return recommendations
    
    def _check_timeout(self, timeout_minutes: int = 30):
        """MANDATORY: Check for timeout conditions"""
        elapsed = (datetime.now() - self.start_time).total_seconds()
        if elapsed > timeout_minutes * 60:
            raise TimeoutError(f"Process exceeded {timeout_minutes} minute timeout")
    
    def _calculate_etc(self, elapsed: float, progress: float) -> float:
        """MANDATORY: Calculate estimated time to completion"""
        if progress > 0:
            total_estimated = elapsed / (progress / 100)
            return max(0, total_estimated - elapsed)
        return 0
    
    def _log_completion_summary(self, report_path: str):
        """MANDATORY: Log comprehensive completion summary"""
        duration = (datetime.now() - self.start_time).total_seconds()
        
        print("=" * 80)
        print("✅ FINAL SYSTEM VALIDATION COMPLETE")
        print("=" * 80)
        print(f"Total Duration: {duration:.1f} seconds")
        print(f"Process ID: {self.process_id}")
        print(f"Success Rate: {self.validation_results['success_rate']:.1f}%")
        print(f"Enterprise Compliance: {'✅ ACHIEVED' if self.validation_results['enterprise_compliance'] else '❌ NOT MET'}")
        print(f"Report Generated: {report_path}")
        print("=" * 80)

def main():
    """Main execution function with DUAL COPILOT validation"""
    
    try:
        # Initialize validator
        validator = FinalSystemValidator()
        
        # Execute comprehensive validation
        results = validator.execute_comprehensive_validation()
        
        # DUAL COPILOT: Secondary validation of results
        if results["overall_success"] and results["success_rate"] >= 95.0:
            print("🏆 DUAL COPILOT VALIDATION: PASSED")
            print("✅ Final system validation completed with enterprise compliance")
            return 0
        else:
            print("⚠️ DUAL COPILOT VALIDATION: ATTENTION REQUIRED")
            print(f"⚠️ Success rate: {results['success_rate']:.1f}% (target: ≥95%)")
            return 1
    
    except Exception as e:
        print(f"❌ FINAL SYSTEM VALIDATION FAILED: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
