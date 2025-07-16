"""
Deployment validation functionality.
Refactored from original validate_final_deployment.py with enhanced modular design.
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

from ..core.validators import BaseValidator, ValidationResult, ValidationStatus
from ..core.rules import (
    FileExistsRule, DatabaseIntegrityRule, JsonValidRule, 
    ThresholdRule, RuleBasedValidator
)


class DeploymentValidator(BaseValidator):
    """Enhanced deployment validator with comprehensive enterprise checks"""
    
    def __init__(self, workspace_path: Optional[str] = None):
        super().__init__("Deployment Validator")
        self.workspace_path = Path(workspace_path or ".")
        
    def validate(self, target=None) -> ValidationResult:
        """Main deployment validation entry point"""
        return self.validate_final_deployment_status()
    
    def validate_final_deployment_status(self) -> ValidationResult:
        """Validate final enterprise deployment status"""
        print("="*80)
        print("ENTERPRISE DEPLOYMENT COMPLETION VALIDATION")
        print("gh_COPILOT Toolkit v4.0 - Final Status Check")
        print("="*80)
        
        validation_results = {
            "deployment_validation": "IN_PROGRESS",
            "timestamp": datetime.now().isoformat(),
            "validation_components": {}
        }
        
        # Run all validation components
        certificate_result = self._validate_enterprise_certificate()
        database_result = self._validate_database_architecture()
        systems_result = self._validate_autonomous_systems()
        compliance_result = self._validate_compliance_framework()
        readiness_result = self._validate_readiness_status()
        
        # Aggregate results
        component_results = [
            certificate_result,
            database_result,
            systems_result,
            compliance_result,
            readiness_result
        ]
        
        # Determine overall status
        failed_count = sum(1 for r in component_results if r.is_failure)
        warning_count = sum(1 for r in component_results if r.status == ValidationStatus.WARNING)
        passed_count = sum(1 for r in component_results if r.status == ValidationStatus.PASSED)
        
        all_errors = []
        all_warnings = []
        all_details = {}
        
        for result in component_results:
            all_errors.extend(result.errors)
            all_warnings.extend(result.warnings)
            all_details.update(result.details)
        
        if failed_count > 0:
            status = ValidationStatus.FAILED
            message = f"Deployment validation failed: {failed_count} components failed"
            validation_results["deployment_validation"] = "FAILED"
        elif warning_count > 0:
            status = ValidationStatus.WARNING
            message = f"Deployment validation passed with warnings: {warning_count} components have warnings"
            validation_results["deployment_validation"] = "PASSED_WITH_WARNINGS"
        else:
            status = ValidationStatus.PASSED
            message = "Deployment validation passed: All components validated successfully"
            validation_results["deployment_validation"] = "PASSED"
        
        # Save validation results
        self._save_validation_results(validation_results)
        
        print("\n" + "="*80)
        print("ENTERPRISE DEPLOYMENT VALIDATION COMPLETED")
        print("="*80)
        print(f"Status: {validation_results['deployment_validation']}")
        print(f"Components Passed: {passed_count}")
        print(f"Components with Warnings: {warning_count}")
        print(f"Components Failed: {failed_count}")
        print("="*80)
        
        return ValidationResult(
            status=status,
            message=message,
            details={
                'validation_results': validation_results,
                'component_summary': {
                    'passed': passed_count,
                    'warnings': warning_count,
                    'failed': failed_count
                }
            },
            errors=all_errors,
            warnings=all_warnings
        )
    
    def _validate_enterprise_certificate(self) -> ValidationResult:
        """Validate Enterprise Certificate"""
        certificate_path = self.workspace_path / "ENTERPRISE_READINESS_100_PERCENT_CERTIFICATE.json"
        
        if not certificate_path.exists():
            print("✗ Enterprise Certificate: MISSING")
            return ValidationResult(
                status=ValidationStatus.FAILED,
                message="Enterprise certificate missing",
                errors=["ENTERPRISE_READINESS_100_PERCENT_CERTIFICATE.json not found"],
                details={"certificate_path": str(certificate_path)}
            )
        
        try:
            with open(certificate_path, 'r', encoding='utf-8') as f:
                certificate_data = json.load(f)
                
            enterprise_readiness = certificate_data.get("ENTERPRISE_READINESS", {}).get("overall_readiness_percentage", 0)
            
            if enterprise_readiness >= 100.0:
                print(f"✓ Enterprise Certificate: {enterprise_readiness}% Readiness")
                return ValidationResult(
                    status=ValidationStatus.PASSED,
                    message=f"Enterprise certificate valid: {enterprise_readiness}% readiness",
                    details={
                        "readiness_level": f"{enterprise_readiness}%",
                        "certificate_valid": True
                    }
                )
            else:
                print(f"⚠ Enterprise Certificate: {enterprise_readiness}% Readiness (Below 100%)")
                return ValidationResult(
                    status=ValidationStatus.WARNING,
                    message=f"Enterprise certificate readiness below 100%: {enterprise_readiness}%",
                    warnings=[f"Readiness level {enterprise_readiness}% is below required 100%"],
                    details={
                        "readiness_level": f"{enterprise_readiness}%",
                        "certificate_valid": False
                    }
                )
                
        except Exception as e:
            print(f"✗ Enterprise Certificate Error: {e}")
            return ValidationResult(
                status=ValidationStatus.ERROR,
                message=f"Enterprise certificate validation error: {str(e)}",
                errors=[str(e)]
            )
    
    def _validate_database_architecture(self) -> ValidationResult:
        """Validate Database Architecture"""
        production_db = self.workspace_path / "production.db"
        
        if not production_db.exists():
            print("✗ Database Architecture: MISSING")
            return ValidationResult(
                status=ValidationStatus.FAILED,
                message="Production database missing",
                errors=["production.db not found"]
            )
        
        try:
            with sqlite3.connect(str(production_db)) as conn:
                cursor = conn.cursor()
                
                # Check integrity
                cursor.execute("PRAGMA integrity_check")
                integrity_result = cursor.fetchone()[0]
                
                # Count tables
                cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
                table_count = cursor.fetchone()[0]
                
            print(f"✓ Database Architecture: {table_count} tables, integrity: {integrity_result}")
            
            if integrity_result == 'ok':
                return ValidationResult(
                    status=ValidationStatus.PASSED,
                    message=f"Database architecture healthy: {table_count} tables",
                    details={
                        "integrity": integrity_result,
                        "table_count": table_count,
                        "database_healthy": True
                    }
                )
            else:
                return ValidationResult(
                    status=ValidationStatus.WARNING,
                    message=f"Database integrity issues: {integrity_result}",
                    warnings=[f"Database integrity check result: {integrity_result}"],
                    details={
                        "integrity": integrity_result,
                        "table_count": table_count,
                        "database_healthy": False
                    }
                )
                
        except Exception as e:
            print(f"✗ Database Architecture Error: {e}")
            return ValidationResult(
                status=ValidationStatus.ERROR,
                message=f"Database architecture validation error: {str(e)}",
                errors=[str(e)]
            )
    
    def _validate_autonomous_systems(self) -> ValidationResult:
        """Validate Autonomous Systems"""
        autonomous_systems = [
            "autonomous_monitoring_system.py",
            "execute_enterprise_audit.py", 
            "optimize_to_100_percent.py"
        ]
        
        missing_systems = []
        present_systems = []
        
        for system_file in autonomous_systems:
            system_path = self.workspace_path / system_file
            if system_path.exists():
                present_systems.append(system_file)
                print(f"✓ Autonomous System: {system_file}")
            else:
                missing_systems.append(system_file)
                print(f"✗ Autonomous System: {system_file} MISSING")
        
        if missing_systems:
            return ValidationResult(
                status=ValidationStatus.WARNING,
                message=f"Some autonomous systems missing: {len(missing_systems)}/{len(autonomous_systems)}",
                warnings=[f"Missing system: {system}" for system in missing_systems],
                details={
                    "present_systems": present_systems,
                    "missing_systems": missing_systems,
                    "total_systems": len(autonomous_systems)
                }
            )
        else:
            return ValidationResult(
                status=ValidationStatus.PASSED,
                message=f"All autonomous systems present: {len(present_systems)}/{len(autonomous_systems)}",
                details={
                    "present_systems": present_systems,
                    "missing_systems": [],
                    "total_systems": len(autonomous_systems)
                }
            )
    
    def _validate_compliance_framework(self) -> ValidationResult:
        """Validate Compliance Framework"""
        # Check for compliance-related files and configurations
        compliance_files = [
            ".flake8",
            "pytest.ini",
            "requirements.txt"
        ]
        
        missing_compliance = []
        present_compliance = []
        
        for compliance_file in compliance_files:
            compliance_path = self.workspace_path / compliance_file
            if compliance_path.exists():
                present_compliance.append(compliance_file)
                print(f"✓ Compliance: {compliance_file}")
            else:
                missing_compliance.append(compliance_file)
                print(f"✗ Compliance: {compliance_file} MISSING")
        
        if missing_compliance:
            return ValidationResult(
                status=ValidationStatus.WARNING,
                message=f"Some compliance files missing: {len(missing_compliance)}/{len(compliance_files)}",
                warnings=[f"Missing compliance file: {file}" for file in missing_compliance],
                details={
                    "present_compliance": present_compliance,
                    "missing_compliance": missing_compliance
                }
            )
        else:
            return ValidationResult(
                status=ValidationStatus.PASSED,
                message="Compliance framework complete",
                details={
                    "present_compliance": present_compliance,
                    "missing_compliance": []
                }
            )
    
    def _validate_readiness_status(self) -> ValidationResult:
        """Validate Overall Readiness Status"""
        readiness_marker = self.workspace_path / "ENTERPRISE_READINESS_100_PERCENT_ACHIEVED.marker"
        
        if readiness_marker.exists():
            print("✓ Readiness Status: 100% ACHIEVED")
            return ValidationResult(
                status=ValidationStatus.PASSED,
                message="Enterprise readiness 100% achieved",
                details={"readiness_marker": True}
            )
        else:
            print("⚠ Readiness Status: MARKER MISSING")
            return ValidationResult(
                status=ValidationStatus.WARNING,
                message="Enterprise readiness marker missing",
                warnings=["ENTERPRISE_READINESS_100_PERCENT_ACHIEVED.marker not found"],
                details={"readiness_marker": False}
            )
    
    def _save_validation_results(self, results: Dict[str, Any]):
        """Save validation results to file"""
        try:
            output_file = self.workspace_path / "FINAL_DEPLOYMENT_VALIDATION.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"✓ Validation results saved to: {output_file}")
        except Exception as e:
            print(f"⚠ Could not save validation results: {e}")


def main():
    """Main execution function - maintains backward compatibility"""
    validator = DeploymentValidator()
    result = validator.validate_final_deployment_status()
    
    return result.is_success


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)