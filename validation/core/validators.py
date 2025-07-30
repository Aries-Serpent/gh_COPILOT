"""
Base validation classes and result structures.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List
from enum import Enum
import logging
from datetime import datetime


class ValidationStatus(Enum):
    """Validation status enumeration"""
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class ValidationResult:
    """Result of a validation operation"""
    status: ValidationStatus
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def is_success(self) -> bool:
        """Check if validation was successful"""
        return self.status in [ValidationStatus.PASSED, ValidationStatus.WARNING]

    @property
    def is_failure(self) -> bool:
        """Check if validation failed"""
        return self.status in [ValidationStatus.FAILED, ValidationStatus.ERROR]


class BaseValidator(ABC):
    """Base class for all validators"""

    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def validate(self, target: Any) -> ValidationResult:
        """Perform validation on target - must be implemented by subclasses"""
        pass

    def pre_validate(self, target: Any) -> bool:
        """Pre-validation hook - return False to skip validation"""
        return True

    def post_validate(self, result: ValidationResult) -> ValidationResult:
        """Post-validation hook - allows result modification"""
        return result

    def run_validation(self, target: Any) -> ValidationResult:
        """Run full validation with pre/post hooks"""
        try:
            # Pre-validation check
            if not self.pre_validate(target):
                return ValidationResult(
                    status=ValidationStatus.SKIPPED,
                    message=f"Validation skipped for {self.name}"
                )

            # Main validation
            result = self.validate(target)

            # Post-validation processing
            result = self.post_validate(result)

            # Log result
            self._log_result(result)

            return result

        except Exception as e:
            error_result = ValidationResult(
                status=ValidationStatus.ERROR,
                message=f"Validation error in {self.name}: {str(e)}",
                errors=[str(e)]
            )
            self._log_result(error_result)
            return error_result

    def _log_result(self, result: ValidationResult):
        """Log validation result"""
        if result.status == ValidationStatus.PASSED:
            self.logger.info(f"✓ {self.name}: {result.message}")
        elif result.status == ValidationStatus.WARNING:
            self.logger.warning(f"⚠ {self.name}: {result.message}")
        elif result.status == ValidationStatus.FAILED:
            self.logger.error(f"✗ {self.name}: {result.message}")
        elif result.status == ValidationStatus.ERROR:
            self.logger.error(f"💥 {self.name}: {result.message}")
        elif result.status == ValidationStatus.SKIPPED:
            self.logger.info(f"⏭ {self.name}: {result.message}")


class CompositeValidator(BaseValidator):
    """Validator that runs multiple validators"""

    def __init__(self, name: str, validators: List[BaseValidator]):
        super().__init__(name)
        self.validators = validators

    def validate(self, target: Any) -> ValidationResult:
        """Run all validators and aggregate results"""
        results = []
        all_errors = []
        all_warnings = []
        all_details = {}

        for validator in self.validators:
            result = validator.run_validation(target)
            results.append(result)
            all_errors.extend(result.errors)
            all_warnings.extend(result.warnings)
            all_details[validator.name] = result.details

        # Determine overall status
        failed_count = sum(1 for r in results if r.is_failure)
        warning_count = sum(1 for r in results if r.status == ValidationStatus.WARNING)

        if failed_count > 0:
            status = ValidationStatus.FAILED
            message = f"Composite validation failed: {failed_count}/{len(results)} validators failed"
        elif warning_count > 0:
            status = ValidationStatus.WARNING
            message = (
                f"Composite validation passed with warnings: {warning_count}/"
                f"{len(results)} validators had warnings"
            )
        else:
            status = ValidationStatus.PASSED
            message = f"Composite validation passed: {len(results)}/{len(results)} validators passed"

        return ValidationResult(
            status=status,
            message=message,
            details=all_details,
            errors=all_errors,
            warnings=all_warnings
        )
