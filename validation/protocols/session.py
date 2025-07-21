"""
Session protocol validation functionality.
Refactored from original session_protocol_validator.py with enhanced modular design.
"""

import logging
import os
from typing import Optional

from copilot.common.workspace_utils import get_workspace_path
from ..core.validators import BaseValidator, ValidationResult, ValidationStatus
from ..core.rules import NoZeroByteFilesRule, RuleBasedValidator

# Text-based indicators (NO Unicode emojis)
TEXT_INDICATORS = {
    'start': '[START]',
    'success': '[SUCCESS]',
    'error': '[ERROR]',
    'info': '[INFO]'
}


class SessionProtocolValidator(BaseValidator):
    """Enhanced session protocol validator.

    Checks include:
    - workspace integrity and zero-byte files
    - session cleanup and permissions
    - credential sanitization
    - session timeout enforcement
    - secure connection requirements
    """

    def __init__(self, workspace_path: Optional[str] = None):
        super().__init__("Session Protocol Validator")
        self.workspace_path = get_workspace_path(workspace_path)
        self.logger = logging.getLogger(__name__)

    def validate(self, target=None) -> ValidationResult:
        """Validate session protocol compliance"""
        return self.validate_startup()

    def validate_startup(self) -> ValidationResult:
        """Return validation result for workspace integrity on startup."""
        self.logger.info(
            f"{TEXT_INDICATORS['start']} Validating {self.workspace_path}")
        
        # Use rule-based validation
        rules = [
            NoZeroByteFilesRule(self.workspace_path)
        ]
        
        rule_validator = RuleBasedValidator("workspace_integrity", rules)
        result = rule_validator.run_validation(self.workspace_path)
        
        # Add session-specific details
        result.details.update({
            'workspace_path': str(self.workspace_path),
            'validation_type': 'session_startup'
        })
        
        if result.is_success:
            self.logger.info(f"{TEXT_INDICATORS['success']} Session validation passed")
        else:
            self.logger.error(f"{TEXT_INDICATORS['error']} Session validation failed")
            
        return result

    def validate_session_cleanup(self) -> ValidationResult:
        """Validate session cleanup requirements"""
        try:
            temp_files = list(self.workspace_path.glob("*.tmp"))
            lock_files = list(self.workspace_path.glob("*.lock"))
            cache_files = list(self.workspace_path.rglob("__pycache__"))
            
            cleanup_issues = []
            
            if temp_files:
                cleanup_issues.append(f"Found {len(temp_files)} temporary files")
            if lock_files:
                cleanup_issues.append(f"Found {len(lock_files)} lock files")
            if cache_files:
                cleanup_issues.append(f"Found {len(cache_files)} cache directories")
            
            if cleanup_issues:
                return ValidationResult(
                    status=ValidationStatus.WARNING,
                    message="Session cleanup recommended",
                    warnings=cleanup_issues,
                    details={
                        'temp_files': len(temp_files),
                        'lock_files': len(lock_files),
                        'cache_files': len(cache_files)
                    }
                )
            else:
                return ValidationResult(
                    status=ValidationStatus.PASSED,
                    message="Session cleanup validation passed"
                )
                
        except Exception as e:
            return ValidationResult(
                status=ValidationStatus.ERROR,
                message=f"Session cleanup validation failed: {str(e)}",
                errors=[str(e)]
            )

    def validate_session_permissions(self) -> ValidationResult:
        """Validate session has required permissions"""
        try:
            # Test write permissions
            test_file = self.workspace_path / ".permission_test"
            try:
                test_file.write_text("test")
                test_file.unlink()
                write_permission = True
            except Exception:
                write_permission = False
            
            # Test read permissions
            try:
                list(self.workspace_path.iterdir())
                read_permission = True
            except Exception:
                read_permission = False
            
            issues = []
            if not write_permission:
                issues.append("No write permission in workspace")
            if not read_permission:
                issues.append("No read permission in workspace")
            
            if issues:
                return ValidationResult(
                    status=ValidationStatus.FAILED,
                    message="Session permission validation failed",
                    errors=issues,
                    details={
                        'write_permission': write_permission,
                        'read_permission': read_permission
                    }
                )
            else:
                return ValidationResult(
                    status=ValidationStatus.PASSED,
                    message="Session permission validation passed",
                    details={
                        'write_permission': write_permission,
                        'read_permission': read_permission
                    }
                )
                
        except Exception as e:
            return ValidationResult(
                status=ValidationStatus.ERROR,
                message=f"Session permission validation failed: {str(e)}",
                errors=[str(e)]
            )

    def validate_credential_sanitization(self) -> ValidationResult:
        """Check for sensitive credentials in environment variables."""
        sensitive_keys = [
            k for k in os.environ
            if any(sub in k.lower() for sub in ["password", "secret", "token"])
        ]
        leaked = {k: os.environ[k] for k in sensitive_keys if os.environ.get(k)}

        if leaked:
            return ValidationResult(
                status=ValidationStatus.FAILED,
                message="Sensitive credentials detected",
                errors=[f"{k} present" for k in leaked],
                details=leaked,
            )

        return ValidationResult(
            status=ValidationStatus.PASSED,
            message="Credential sanitization passed",
        )

    def validate_session_timeout(self) -> ValidationResult:
        """Ensure SESSION_TIMEOUT <= 24 hours."""
        timeout = os.getenv("SESSION_TIMEOUT")
        try:
            hours = float(timeout) if timeout else 1.0
        except ValueError:
            return ValidationResult(
                status=ValidationStatus.ERROR,
                message="Invalid SESSION_TIMEOUT",
                errors=[f"value: {timeout}"],
            )

        if hours > 24:
            return ValidationResult(
                status=ValidationStatus.FAILED,
                message="Session timeout exceeds limit",
                details={"timeout_hours": hours},
            )

        return ValidationResult(
            status=ValidationStatus.PASSED,
            message="Session timeout within limits",
            details={"timeout_hours": hours},
        )

    def validate_secure_connection(self) -> ValidationResult:
        """Require HTTPS for secure sessions."""
        use_https = os.getenv("USE_HTTPS", "1") == "1"
        if not use_https:
            return ValidationResult(
                status=ValidationStatus.FAILED,
                message="HTTPS is required",
            )
        return ValidationResult(
            status=ValidationStatus.PASSED,
            message="Secure connection enforced",
        )

    def validate_comprehensive_session(self) -> ValidationResult:
        """Run comprehensive session validation"""
        validators = [
            self,  # Startup validation
        ]
        
        # Create composite validator for comprehensive check
        from ..core.validators import CompositeValidator
        CompositeValidator("comprehensive_session", validators)
        
        # Add additional checks
        startup_result = self.validate_startup()
        cleanup_result = self.validate_session_cleanup()
        permission_result = self.validate_session_permissions()
        credential_result = self.validate_credential_sanitization()
        timeout_result = self.validate_session_timeout()
        secure_result = self.validate_secure_connection()
        
        # Aggregate results
        all_results = [
            startup_result,
            cleanup_result,
            permission_result,
            credential_result,
            timeout_result,
            secure_result,
        ]
        errors = []
        warnings = []
        details = {}
        
        for i, result in enumerate(all_results):
            errors.extend(result.errors)
            warnings.extend(result.warnings)
            details[f"check_{i}"] = result.details
        
        # Determine overall status
        failed_count = sum(1 for r in all_results if r.is_failure)
        warning_count = sum(1 for r in all_results if r.status == ValidationStatus.WARNING)
        
        if failed_count > 0:
            status = ValidationStatus.FAILED
            message = f"Comprehensive session validation failed: {failed_count} checks failed"
        elif warning_count > 0:
            status = ValidationStatus.WARNING
            message = "Comprehensive session validation passed with warnings"
        else:
            status = ValidationStatus.PASSED
            message = "Comprehensive session validation passed"
        
        return ValidationResult(
            status=status,
            message=message,
            details=details,
            errors=errors,
            warnings=warnings
        )


def main():
    """Main execution function - maintains backward compatibility"""
    validator = SessionProtocolValidator()
    result = validator.validate_startup()
    
    if result.is_success:
        print(f"{TEXT_INDICATORS['success']} Session protocol validation passed")
        return True
    else:
        print(f"{TEXT_INDICATORS['error']} Session protocol validation failed")
        for error in result.errors:
            print(f"  Error: {error}")
        return False


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)