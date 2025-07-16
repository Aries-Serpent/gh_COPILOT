#!/usr/bin/env python3
"""
🔍 Configuration Dependency Validator
Validates that all configuration files are accessible from their current locations
Ensures no functionality was broken by file movements
"""

import os
import sys
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from tqdm import tqdm

class ConfigDependencyValidator:
    """🔍 Validates configuration file accessibility and dependencies"""
    
    def __init__(self, workspace_path: Optional[str] = None):
        """Initialize validator with workspace path"""
        self.workspace_path = Path(workspace_path) if workspace_path else Path(os.getenv("GH_COPILOT_WORKSPACE", "e:/gh_COPILOT"config/ "config"
        self.production_db = self.workspace_path / "production.db"
        self.validation_results = {
            "config_files_accessible": [],
            "config_files_missing": [],
            "scripts_with_dependencies": [],
            "broken_dependencies": [],
            "validation_timestamp": datetime.now().isoformat()
        }
        
    def validate_config_accessibility(self) -> Dict[str, Any]:
        """🔍 Validate all configuration files are accessible"""
        print(f"🚀 CONFIG DEPENDENCY VALIDATION STARTED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        with tqdm(total=100, desc="🔍 Config Validation", unit="%") as pbar:
            
            # Phase 1: Check config directory existence (20%)
            pbar.set_description("📁 Checking config directory")
            if not self.config_dir.exists():
                raise RuntimeError(f"Config directory not found: {self.config_dir}")
            pbar.update(20)
            
            # Phase 2: Enumerate config files (20%)
            pbar.set_description("📋 Enumerating config files")
            config_files = list(self.config_dir.glob("*.json"))
            self.validation_results["total_config_files"] = len(config_files)
            pbar.update(20)
            
            # Phase 3: Test config file accessibility (30%)
            pbar.set_description("🔍 Testing file accessibility")
            for config_file in config_files:
                try:
                    # Test file readability
                    with open(config_file, 'r') as f:
                        json.load(f)
                    self.validation_results["config_files_accessible"].append(str(config_file.name))
                except Exception as e:
                    self.validation_results["config_files_missing"].append({
                        "file": str(config_file.name),
                        "error": str(e)
                    })
            pbar.update(30)
            
            # Phase 4: Check COPILOT_NAVIGATION_MAP.json (20%)
            pbar.set_description("🗺️ Checking navigation map")
            nav_map = self.workspace_path / "COPILOT_NAVIGATION_MAP.json"
            if nav_map.exists():
                try:
                    with open(nav_map, 'r') as f:
                        json.load(f)
                    self.validation_results["navigation_map_status"] = "accessible"
                except Exception as e:
                    self.validation_results["navigation_map_status"] = f"error: {e}"
            else:
                self.validation_results["navigation_map_status"] = "missing"
            pbar.update(20)
            
            # Phase 5: Summary (10%)
            pbar.set_description("📊 Generating summary")
            self.validation_results["accessibility_rate"] = (
                len(self.validation_results["config_files_accessible"]) / 
                len(config_files) * 100 if config_files else 0
            )
            pbar.update(10)
        
        return self.validation_results
    
    def test_config_loading_patterns(self) -> Dict[str, Any]:
        """🧪 Test common configuration loading patterns"""
        print("🧪 Testing configuration loading patterns...")
        
        test_results: Dict[str, Any] = {
            "relative_path_loading": False,
            "absolute_path_loading": False,
            "dynamic_path_resolution": False,
            "config_dir_access": False
        }
        
        with tqdm(total=100, desc="🧪 Testing Patterns", unit="%") as pbar:
            
            # Test 1: Relative path loading (25%)
            pbar.set_description("📂 Testing relative paths"config/ "config/advanced_features_config.json"
                if test_file.exists():
                    with open(test_file, 'r') as f:
                        json.load(f)
                    test_results["relative_path_loading"] = True
            except Exception as e:
                test_results["relative_path_error"] = str(e)
            pbar.update(25)
            
            # Test 2: Absolute path loading (25%)
            pbar.set_description("🎯 Testing absolute paths")
            try:
                test_file = self.workspace_path / "config" / "config/replication_config.json"
                if test_file.exists():
                    with open(test_file, 'r') as f:
                        json.load(f)
                    test_results["absolute_path_loading"] = True
            except Exception as e:
                test_results["absolute_path_error"] = str(e)
            pbar.update(25)
            
            # Test 3: Dynamic path resolution (25%)
            pbar.set_description("🔄 Testing dynamic resolution")
            try:
                # Test environment variable based resolution
                workspace = os.getenv("GH_COPILOT_WORKSPACE"config/ "config" / "config/enterprise_master_config.json"
                if config_path.exists():
                    with open(config_path, 'r') as f:
                        json.load(f)
                    test_results["dynamic_path_resolution"] = True
            except Exception as e:
                test_results["dynamic_path_error"] = str(e)
            pbar.update(25)
            
            # Test 4: Config directory enumeration (25%)
            pbar.set_description("📁 Testing directory access")
            try:
                config_files = list(self.config_dir.glob("*.json"))
                if config_files:
                    test_results["config_dir_access"] = True
                    test_results["config_file_count"] = len(config_files)
            except Exception as e:
                test_results["config_dir_error"] = str(e)
            pbar.update(25)
        
        return test_results
    
    def validate_critical_config_files(self) -> Dict[str, Any]:
        """🎯 Validate specific critical configuration files"""
        print("🎯 Validating critical configuration files...")
        
        critical_configs = [
            "config/advanced_features_config.json",
            "config/replication_config.json", 
            "config/enterprise_master_config.json",
            "config/production_access_config.json",
            "config/enterprise_quantum_config.json"
        ]
        
        critical_results = {
            "critical_files_status": {},
            "all_critical_accessible": True,
            "missing_critical_files": []
        }
        
        with tqdm(total=len(critical_configs), desc="🎯 Critical Files", unit="files") as pbar:
            for config_file in critical_configs:
                pbar.set_description(f"🔍 {config_file[:20]}...")
                
                config_path = self.config_dir / config_file
                if config_path.exists():
                    try:
                        with open(config_path, 'r') as f:
                            config_data = json.load(f)
                        
                        critical_results["critical_files_status"][config_file] = {
                            "status": "accessible",
                            "path": str(config_path),
                            "size_bytes": config_path.stat().st_size,
                            "keys_count": len(config_data) if isinstance(config_data, dict) else "N/A"
                        }
                    except Exception as e:
                        critical_results["critical_files_status"][config_file] = {
                            "status": "error",
                            "error": str(e)
                        }
                        critical_results["all_critical_accessible"] = False
                else:
                    critical_results["critical_files_status"][config_file] = {
                        "status": "missing"
                    }
                    critical_results["missing_critical_files"].append(config_file)
                    critical_results["all_critical_accessible"] = False
                
                pbar.update(1)
        
        return critical_results
    
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """📊 Generate comprehensive validation report"""
        print("📊 Generating comprehensive validation report...")
        
        # Run all validations
        accessibility_results = self.validate_config_accessibility()
        pattern_results = self.test_config_loading_patterns()
        critical_results = self.validate_critical_config_files()
        
        # Combine results
        comprehensive_report = {
            "validation_summary": {
                "timestamp": datetime.now().isoformat(),
                "workspace_path": str(self.workspace_path),
                "config_directory": str(self.config_dir),
                "validation_status": "COMPLETED"
            },
            "accessibility_validation": accessibility_results,
            "pattern_testing": pattern_results,
            "critical_files_validation": critical_results,
            "overall_status": {
                "config_accessibility_rate": accessibility_results.get("accessibility_rate", 0),
                "critical_files_accessible": critical_results.get("all_critical_accessible", False),
                "pattern_tests_passed": sum(1 for v in pattern_results.values() if v is True),
                "navigation_map_status": accessibility_results.get("navigation_map_status", "unknown")
            }
        }
        
        # Determine overall health
        if (comprehensive_report["overall_status"]["config_accessibility_rate"] >= 95 and
            comprehensive_report["overall_status"]["critical_files_accessible"] and
            comprehensive_report["overall_status"]["pattern_tests_passed"] >= 2):
            comprehensive_report["overall_status"]["health_status"] = "EXCELLENT"
        elif comprehensive_report["overall_status"]["config_accessibility_rate"] >= 80:
            comprehensive_report["overall_status"]["health_status"] = "GOOD"
        else:
            comprehensive_report["overall_status"]["health_status"] = "NEEDS_ATTENTION"
        
        return comprehensive_report
    
    def save_validation_report(self, report: Dict[str, Any]) -> str:
        """💾 Save validation report to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = self.workspace_path / f"config_dependency_validation_report_{timestamp}.json"
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"✅ Validation report saved: {report_path}")
        return str(report_path)

def main():
    """🚀 Main execution function"""
    print("="*80)
    print("🔍 CONFIGURATION DEPENDENCY VALIDATION")
    print("="*80)
    
    try:
        # Initialize validator
        validator = ConfigDependencyValidator()
        
        # Generate comprehensive report
        report = validator.generate_comprehensive_report()
        
        # Save report
        report_path = validator.save_validation_report(report)
        
        # Print summary
        print("\n" + "="*80)
        print("📊 VALIDATION SUMMARY")
        print("="*80)
        print(f"Config Accessibility Rate: {report['overall_status']['config_accessibility_rate']:.1f}%")
        print(f"Critical Files Accessible: {'✅ YES' if report['overall_status']['critical_files_accessible'] else '❌ NO'}")
        print(f"Pattern Tests Passed: {report['overall_status']['pattern_tests_passed']}/4")
        print(f"Navigation Map Status: {report['overall_status']['navigation_map_status']}")
        print(f"Overall Health: {report['overall_status']['health_status']}")
        print(f"Report Location: {report_path}")
        
        if report['overall_status']['health_status'] == 'EXCELLENT':
            print("\n✅ ALL CONFIGURATION FILES VALIDATED - NO FUNCTIONALITY ISSUES DETECTED")
        else:
            print("\n⚠️ CONFIGURATION ISSUES DETECTED - REVIEW REPORT FOR DETAILS")
        
        return report['overall_status']['health_status'] == 'EXCELLENT'
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
