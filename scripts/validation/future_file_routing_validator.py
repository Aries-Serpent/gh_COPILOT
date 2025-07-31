#!/usr/bin/env python3
"""
🚀 FUTURE FILE ROUTING VALIDATOR
==================================
Validates that all future file operations correctly route files to appropriate folders:
- Log files → logs/ folder
- Report files → reports/ folder  
- Result files → results/ folder
- Documentation files → documentation/ folder
- Configuration files → config/ folder
- Archive files → archives/ folder

Enterprise-grade validation with pattern recognition and workflow testing.
"""

import sys
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import re
import shutil

class FutureFileRoutingValidator:
    def __init__(self):
        self.workspace_root = Path("e:/gh_COPILOT")
        self.db_path = self.workspace_root / "production.db"
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.workspace_root / "logs" / "future_routing_validation.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # File routing patterns
        self.routing_patterns = {
            "logs": {
                "extensions": [".log", ".txt"],
                "keywords": ["log", "debug", "trace", "error", "warning", "audit", "session"],
                "patterns": [r".*\.log$", r".*_log\.txt$", r".*\.trace$", r".*debug.*", r".*error.*"],
                "folder": "logs"
            },
            "reports": {
                "extensions": [".json", ".html", ".csv", ".xlsx", ".md"],
                "keywords": ["report", "summary", "analysis", "compliance", "audit", "certificate"],
                "patterns": [r".*_report.*", r".*summary.*", r".*analysis.*", r".*compliance.*"],
                "folder": "reports"
            },
            "results": {
                "extensions": [".json", ".csv", ".txt", ".xml"],
                "keywords": ["result", "output", "data", "findings", "outcome", "metrics"],
                "patterns": [r".*_result.*", r".*_output.*", r".*_data.*", r".*metrics.*"],
                "folder": "results"
            },
            "documentation": {
                "extensions": [".md", ".rst", ".txt", ".pdf", ".docx"],
                "keywords": ["doc", "readme", "guide", "manual", "instruction", "spec"],
                "patterns": [r".*\.md$", r".*readme.*", r".*guide.*", r".*manual.*", r".*spec.*"],
                "folder": "documentation"
            },
            "config": {
                "extensions": [".json", ".yaml", ".yml", ".ini", ".conf", ".cfg"],
                "keywords": ["config", "settings", "parameters", "environment", "setup"],
                "patterns": [r".*config.*", r".*settings.*", r".*\.env$", r".*parameters.*"],
                "folder": "config"
            },
            "archives": {
                "extensions": [".zip", ".tar", ".gz", ".bz2", ".7z", ".backup"],
                "keywords": ["archive", "backup", "old", "deprecated", "historical"],
                "patterns": [r".*\.zip$", r".*\.tar.*", r".*backup.*", r".*archive.*"],
                "folder": "archives"
            }
        }

    def validate_folder_structure(self) -> bool:
        """Validate that all required folders exist and are accessible."""
        self.logger.info("🏗️ Validating folder structure...")
        
        required_folders = ["logs", "reports", "results", "documentation", "config", "archives"]
        missing_folders = []
        
        for folder in required_folders:
            folder_path = self.workspace_root / folder
            if not folder_path.exists():
                missing_folders.append(folder)
                self.logger.warning(f"❌ Missing folder: {folder}")
            else:
                # Test write permissions
                try:
                    test_file = folder_path / ".write_test"
                    test_file.write_text("test")
                    test_file.unlink()
                    self.logger.info(f"✅ Folder accessible: {folder}")
                except Exception as e:
                    self.logger.error(f"❌ Folder not writable: {folder} - {e}")
                    return False
        
        if missing_folders:
            self.logger.error(f"❌ Missing folders: {missing_folders}")
            return False
        
        self.logger.info("✅ All required folders exist and are accessible")
        return True

    def analyze_file_categorization(self, filename: str) -> str:
        """Analyze a filename and determine its correct folder destination."""
        filename_lower = filename.lower()
        
        # Score each category
        category_scores = {}
        
        for category, rules in self.routing_patterns.items():
            score = 0
            
            # Check file extension
            file_ext = Path(filename).suffix.lower()
            if file_ext in rules["extensions"]:
                score += 30
            
            # Check keywords
            for keyword in rules["keywords"]:
                if keyword in filename_lower:
                    score += 20
            
            # Check regex patterns
            for pattern in rules["patterns"]:
                if re.match(pattern, filename_lower):
                    score += 25
            
            category_scores[category] = score
        
        # Return category with highest score
        best_category = max(category_scores, key=lambda k: category_scores[k])
        best_score = category_scores[best_category]
        
        if best_score > 0:
            return best_category
        else:
            return "unknown"

    def test_routing_patterns(self) -> Dict[str, Any]:
        """Test file routing patterns with sample filenames."""
        self.logger.info("🧪 Testing file routing patterns...")
        
        test_cases = {
            # Log files
            "system_startup.log": "logs",
            "debug_session_20250716.log": "logs", 
            "error_trace.txt": "logs",
            "audit_session.log": "logs",
            
            # Report files
            "compliance_report_20250716.json": "reports",
            "performance_analysis.html": "reports",
            "quarterly_summary.csv": "reports",
            "audit_certificate.json": "reports",
            
            # Result files
            "test_results.json": "results",
            "processing_output.csv": "results",
            "analysis_data.xml": "results",
            "performance_metrics.txt": "results",
            
            # Documentation files
            "README.md": "documentation",
            "user_guide.pdf": "documentation",
            "installation_manual.rst": "documentation",
            "api_spec.md": "documentation",
            
            # Configuration files
            "database_config.json": "config",
            "application_settings.yaml": "config",
            "environment_parameters.ini": "config",
            ".env": "config",
            
            # Archive files
            "backup_20250716.zip": "archives",
            "historical_data.tar.gz": "archives",
            "deprecated_files.7z": "archives",
            "old_logs_archive.backup": "archives"
        }
        
        results = {}
        passed_tests = 0
        total_tests = len(test_cases)
        
        for filename, expected_category in test_cases.items():
            predicted_category = self.analyze_file_categorization(filename)
            passed = predicted_category == expected_category
            results[filename] = passed
            
            if passed:
                passed_tests += 1
                self.logger.info(f"✅ {filename} → {predicted_category}")
            else:
                self.logger.warning(f"❌ {filename} → {predicted_category} (expected: {expected_category})")
        
        success_rate = (passed_tests / total_tests) * 100
        self.logger.info(f"📊 Pattern test results: {passed_tests}/{total_tests} ({success_rate:.1f}% success rate)")
        
        return {
            "results": results,
            "success_rate": success_rate,
            "passed": passed_tests,
            "total": total_tests
        }

    def validate_current_file_locations(self) -> Dict[str, List[str]]:
        """Validate that existing files are in their correct locations."""
        self.logger.info("📍 Validating current file locations...")
        
        misplaced_files = {}
        
        for folder in ["logs", "reports", "results", "documentation", "config", "archives"]:
            folder_path = self.workspace_root / folder
            if not folder_path.exists():
                continue
                
            misplaced_files[folder] = []
            
            for file_path in folder_path.rglob("*"):
                if file_path.is_file():
                    predicted_folder = self.analyze_file_categorization(file_path.name)
                    
                    if predicted_folder != folder and predicted_folder != "unknown":
                        misplaced_files[folder].append({
                            "file": file_path.name,
                            "current_folder": folder,
                            "predicted_folder": predicted_folder,
                            "path": str(file_path)
                        })
        
        # Report findings
        total_misplaced = sum(len(files) for files in misplaced_files.values())
        
        if total_misplaced == 0:
            self.logger.info("✅ All files are in their correct locations")
        else:
            self.logger.warning(f"⚠️ Found {total_misplaced} potentially misplaced files")
            for folder, files in misplaced_files.items():
                if files:
                    self.logger.warning(f"  {folder}/: {len(files)} misplaced files")
        
        return misplaced_files

    def create_routing_workflow_test(self) -> bool:
        """Create and test a simulated file routing workflow."""
        self.logger.info("🔄 Testing file routing workflow...")
        
        try:
            # Create temporary test files
            test_files = [
                ("test_log_file.log", "logs"),
                ("test_report.json", "reports"), 
                ("test_results.csv", "results"),
                ("test_documentation.md", "documentation"),
                ("test_config.yaml", "config")
            ]
            
            workflow_results = []
            
            for filename, expected_folder in test_files:
                # Predict destination
                predicted_folder = self.analyze_file_categorization(filename)
                
                # Create test file in root
                test_file_path = self.workspace_root / filename
                test_file_path.write_text(f"Test content for {filename}")
                
                # Simulate routing
                destination_path = self.workspace_root / predicted_folder / filename
                
                # Move file to predicted location
                shutil.move(str(test_file_path), str(destination_path))
                
                # Verify file exists in correct location
                correct_routing = destination_path.exists() and predicted_folder == expected_folder
                
                workflow_results.append({
                    "filename": filename,
                    "expected": expected_folder,
                    "predicted": predicted_folder,
                    "routed_correctly": correct_routing
                })
                
                # Cleanup
                if destination_path.exists():
                    destination_path.unlink()
                
                self.logger.info(f"{'✅' if correct_routing else '❌'} {filename} → {predicted_folder}")
            
            success_count = sum(1 for result in workflow_results if result["routed_correctly"])
            total_count = len(workflow_results)
            
            self.logger.info(f"📊 Workflow test: {success_count}/{total_count} files routed correctly")
            
            return success_count == total_count
            
        except Exception as e:
            self.logger.error(f"❌ Workflow test failed: {e}")
            return False

    def generate_routing_report(self) -> Dict:
        """Generate comprehensive routing validation report."""
        self.logger.info("📋 Generating comprehensive routing validation report...")
        
        # Run all validations
        folder_structure_valid = self.validate_folder_structure()
        pattern_test_results = self.test_routing_patterns()
        current_locations = self.validate_current_file_locations()
        workflow_test_passed = self.create_routing_workflow_test()
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "workspace_root": str(self.workspace_root),
            "validation_results": {
                "folder_structure": {
                    "valid": folder_structure_valid,
                    "status": "PASS" if folder_structure_valid else "FAIL"
                },
                "routing_patterns": {
                    "success_rate": pattern_test_results["success_rate"],
                    "passed_tests": pattern_test_results["passed"],
                    "total_tests": pattern_test_results["total"],
                    "status": "PASS" if pattern_test_results["success_rate"] >= 90 else "FAIL"
                },
                "current_file_locations": {
                    "total_misplaced": sum(len(files) for files in current_locations.values()),
                    "misplaced_files": current_locations,
                    "status": "PASS" if sum(len(files) for files in current_locations.values()) == 0 else "WARNING"
                },
                "workflow_test": {
                    "passed": workflow_test_passed,
                    "status": "PASS" if workflow_test_passed else "FAIL"
                }
            },
            "routing_patterns": self.routing_patterns,
            "overall_status": "PASS" if all([
                folder_structure_valid,
                pattern_test_results["success_rate"] >= 90,
                workflow_test_passed
            ]) else "NEEDS_ATTENTION"
        }
        
        # Save report
        report_path = self.workspace_root / "reports" / f"future_file_routing_validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.logger.info(f"📄 Report saved: {report_path}")
        
        return report

def main():
    """Main execution function."""
    print("🚀 FUTURE FILE ROUTING VALIDATOR")
    print("=" * 50)
    
    validator = FutureFileRoutingValidator()
    
    try:
        # Generate comprehensive validation report
        report = validator.generate_routing_report()
        
        # Display summary
        print(f"\n📊 VALIDATION SUMMARY")
        print(f"Overall Status: {report['overall_status']}")
        print(f"Folder Structure: {report['validation_results']['folder_structure']['status']}")
        print(f"Routing Patterns: {report['validation_results']['routing_patterns']['status']} ({report['validation_results']['routing_patterns']['success_rate']:.1f}%)")
        print(f"Current Locations: {report['validation_results']['current_file_locations']['status']}")
        print(f"Workflow Test: {report['validation_results']['workflow_test']['status']}")
        
        if report['overall_status'] == 'PASS':
            print("\n✅ ALL VALIDATIONS PASSED - Future file routing is properly configured!")
        else:
            print("\n⚠️ SOME VALIDATIONS NEED ATTENTION - Review the report for details")
        
        return report['overall_status'] == 'PASS'
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        validator.logger.error(f"Validation failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
