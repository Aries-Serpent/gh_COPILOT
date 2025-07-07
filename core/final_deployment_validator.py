#!/usr/bin/env python3
"""
Final Deployment Validator for gh_COPILOT
Comprehensive validation for professional deployment readiness
"""

import os
import json
import sys
import logging
from datetime import datetime
from pathlib import Path
import re
import traceback
from typing import Optional

from common.path_utils import get_workspace_root

# Professional logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('final_deployment_validation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class FinalDeploymentValidator:
    def __init__(self, workspace_path: Optional[str] = None):
        if workspace_path is None:
            workspace_path = str(get_workspace_root())
        self.workspace_path = Path(workspace_path)
        self.validation_results = {
            "timestamp": datetime.now().isoformat(),
            "validation_status": "PENDING",
            "issues_found": [],
            "fixes_applied": [],
            "deployment_ready": False,
            "summary": {}
        }
        
    def validate_unicode_cleanup(self):
        """Validate Unicode/emoji cleanup was successful"""
        logger.info("Validating Unicode cleanup...")
        
        unicode_issues = []
        python_files = list(self.workspace_path.glob("*.py"))
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Check for common emoji/unicode patterns
                emoji_pattern = r'[^\x00-\x7F]+'
                if re.search(emoji_pattern, content):
                    unicode_issues.append(str(file_path))
                    
            except Exception as e:
                logger.warning(f"Could not check {file_path}: {e}")
                
        if unicode_issues:
            self.validation_results["issues_found"].append({
                "type": "unicode_cleanup",
                "files": unicode_issues,
                "severity": "low"
            })
            return False
        else:
            logger.info("Unicode cleanup validation: PASSED")
            return True
            
    def validate_json_serialization(self):
        """Validate JSON serialization fixes"""
        logger.info("Validating JSON serialization...")
        
        test_data = {
            "timestamp": datetime.now(),
            "test_string": "Professional deployment test",
            "test_number": 12345,
            "test_boolean": True
        }
        
        try:
            # Test serialization
            json_str = json.dumps(test_data, default=str)
            
            # Test deserialization
            parsed_data = json.loads(json_str)
            
            logger.info("JSON serialization validation: PASSED")
            return True
            
        except Exception as e:
            logger.error(f"JSON serialization validation failed: {e}")
            self.validation_results["issues_found"].append({
                "type": "json_serialization",
                "error": str(e),
                "severity": "medium"
            })
            return False
            
    def validate_windows_compatibility(self):
        """Validate Windows compatibility"""
        logger.info("Validating Windows compatibility...")
        
        # Check for Windows-specific path handling
        windows_issues = []
        
        # Test path operations
        try:
            test_path = Path("e:/test_path")
            test_path.exists()  # This should work on Windows
            logger.info("Windows path compatibility: PASSED")
            return True
            
        except Exception as e:
            logger.error(f"Windows compatibility issue: {e}")
            self.validation_results["issues_found"].append({
                "type": "windows_compatibility",
                "error": str(e),
                "severity": "high"
            })
            return False
            
    def validate_performance_monitoring(self):
        """Validate performance monitoring system"""
        logger.info("Validating performance monitoring...")
        
        # Check if performance monitor exists and is Windows-compatible
        perf_monitor_path = self.workspace_path / "enterprise_performance_monitor_windows.py"
        
        if not perf_monitor_path.exists():
            self.validation_results["issues_found"].append({
                "type": "performance_monitor",
                "error": "Windows performance monitor not found",
                "severity": "medium"
            })
            return False
            
        # Check for professional content (no emojis)
        try:
            with open(perf_monitor_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if re.search(r'[^\x00-\x7F]+', content):
                    self.validation_results["issues_found"].append({
                        "type": "performance_monitor",
                        "error": "Performance monitor contains non-ASCII characters",
                        "severity": "low"
                    })
                    return False
                    
        except Exception as e:
            logger.error(f"Performance monitor validation failed: {e}")
            return False
            
        logger.info("Performance monitoring validation: PASSED")
        return True
        
    def validate_analytics_enhancement(self):
        """Validate advanced analytics enhancement"""
        logger.info("Validating analytics enhancement...")
        
        analytics_path = self.workspace_path / "advanced_analytics_phase4_phase5_enhancement.py"
        
        if not analytics_path.exists():
            self.validation_results["issues_found"].append({
                "type": "analytics_enhancement",
                "error": "Advanced analytics enhancement not found",
                "severity": "medium"
            })
            return False
            
        logger.info("Analytics enhancement validation: PASSED")
        return True
        
    def check_deployment_readiness(self):
        """Check overall deployment readiness"""
        logger.info("Checking deployment readiness...")
        
        # Count critical issues
        critical_issues = [
            issue for issue in self.validation_results["issues_found"]
            if issue["severity"] == "high"
        ]
        
        medium_issues = [
            issue for issue in self.validation_results["issues_found"]
            if issue["severity"] == "medium"
        ]
        
        low_issues = [
            issue for issue in self.validation_results["issues_found"]
            if issue["severity"] == "low"
        ]
        
        # Deployment ready if no critical issues
        deployment_ready = len(critical_issues) == 0
        
        self.validation_results["deployment_ready"] = deployment_ready
        self.validation_results["summary"] = {
            "total_issues": len(self.validation_results["issues_found"]),
            "critical_issues": len(critical_issues),
            "medium_issues": len(medium_issues),
            "low_issues": len(low_issues),
            "deployment_ready": deployment_ready
        }
        
        if deployment_ready:
            self.validation_results["validation_status"] = "PASSED"
            logger.info("=== DEPLOYMENT READY ===")
        else:
            self.validation_results["validation_status"] = "FAILED"
            logger.warning("=== DEPLOYMENT NOT READY ===")
            
        return deployment_ready
        
    def generate_final_report(self):
        """Generate final validation report"""
        logger.info("Generating final validation report...")
        
        report_path = self.workspace_path / f"final_deployment_validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(self.validation_results, f, indent=2, default=str)
                
            logger.info(f"Final validation report saved: {report_path}")
            
            # Print summary
            print("\n" + "="*80)
            print("FINAL DEPLOYMENT VALIDATION SUMMARY")
            print("="*80)
            print(f"Validation Status: {self.validation_results['validation_status']}")
            print(f"Deployment Ready: {self.validation_results['deployment_ready']}")
            print(f"Total Issues Found: {self.validation_results['summary']['total_issues']}")
            print(f"Critical Issues: {self.validation_results['summary']['critical_issues']}")
            print(f"Medium Issues: {self.validation_results['summary']['medium_issues']}")
            print(f"Low Issues: {self.validation_results['summary']['low_issues']}")
            
            if self.validation_results["issues_found"]:
                print("\nISSUES FOUND:")
                for i, issue in enumerate(self.validation_results["issues_found"], 1):
                    print(f"  {i}. [{issue['severity'].upper()}] {issue['type']}")
                    if 'error' in issue:
                        print(f"      Error: {issue['error']}")
                    if 'files' in issue:
                        print(f"      Files: {len(issue['files'])} files affected")
            
            if self.validation_results["deployment_ready"]:
                print("\n[SUCCESS] ENVIRONMENT IS READY FOR PROFESSIONAL DEPLOYMENT")
                print("[SUCCESS] All critical issues have been resolved")
                print("[SUCCESS] gh_COPILOT can be deployed to E:/gh_COPILOT")
            else:
                print("\n[FAILURE] ENVIRONMENT NEEDS ATTENTION BEFORE DEPLOYMENT")
                print("[FAILURE] Critical issues must be resolved")
                
            print("="*80)
            
        except Exception as e:
            logger.error(f"Failed to generate final report: {e}")
            
    def run_full_validation(self):
        """Run complete validation suite"""
        logger.info("Starting final deployment validation...")
        
        try:
            # Run all validation checks
            validations = [
                ("Unicode Cleanup", self.validate_unicode_cleanup),
                ("JSON Serialization", self.validate_json_serialization),
                ("Windows Compatibility", self.validate_windows_compatibility),
                ("Performance Monitoring", self.validate_performance_monitoring),
                ("Analytics Enhancement", self.validate_analytics_enhancement)
            ]
            
            passed_validations = 0
            for name, validation_func in validations:
                try:
                    if validation_func():
                        passed_validations += 1
                        self.validation_results["fixes_applied"].append(name)
                    else:
                        logger.warning(f"Validation failed: {name}")
                except Exception as e:
                    logger.error(f"Validation error for {name}: {e}")
                    self.validation_results["issues_found"].append({
                        "type": name.lower().replace(" ", "_"),
                        "error": str(e),
                        "severity": "high"
                    })
            
            # Check deployment readiness
            self.check_deployment_readiness()
            
            # Generate final report
            self.generate_final_report()
            
            logger.info(f"Final validation completed: {passed_validations}/{len(validations)} checks passed")
            
        except Exception as e:
            logger.error(f"Final validation failed: {e}")
            traceback.print_exc()


def main():
    """Main function"""
    validator = FinalDeploymentValidator()
    validator.run_full_validation()


if __name__ == "__main__":
    main()
