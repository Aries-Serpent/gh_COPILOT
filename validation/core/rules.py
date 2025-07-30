"""
Validation rule definitions and implementations.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, List
import sqlite3
import json

from .validators import BaseValidator, ValidationResult, ValidationStatus


class ValidationRule(ABC):
    """Base class for validation rules"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    def check(self, target: Any) -> bool:
        """Check if the rule passes"""
        pass

    def get_failure_message(self, target: Any) -> str:
        """Get message when rule fails"""
        return f"Rule '{self.name}' failed"


class FileExistsRule(ValidationRule):
    """Rule to check if a file exists"""

    def __init__(self, file_path: str):
        super().__init__(
            name=f"file_exists_{Path(file_path).name}",
            description=f"Check if file {file_path} exists"
        )
        self.file_path = Path(file_path)

    def check(self, target: Any) -> bool:
        return self.file_path.exists()

    def get_failure_message(self, target: Any) -> str:
        return f"Required file {self.file_path} does not exist"


class NoZeroByteFilesRule(ValidationRule):
    """Rule to check for zero-byte files in a directory"""

    def __init__(self, directory: Path):
        super().__init__(
            name="no_zero_byte_files",
            description=f"Check for zero-byte files in {directory}"
        )
        self.directory = directory
        self.zero_byte_files = []

    def check(self, target: Any) -> bool:
        self.zero_byte_files = []

        if not self.directory.exists():
            return True  # Can't have zero-byte files if directory doesn't exist

        for path in self.directory.rglob('*'):
            if path.is_file() and path.stat().st_size == 0:
                self.zero_byte_files.append(path)

        return len(self.zero_byte_files) == 0

    def get_failure_message(self, target: Any) -> str:
        files_preview = ", ".join(str(f) for f in self.zero_byte_files[:5])
        return f"Found {len(self.zero_byte_files)} zero-byte files: {files_preview}"


class DatabaseIntegrityRule(ValidationRule):
    """Rule to check database integrity"""

    def __init__(self, database_path: Path):
        super().__init__(
            name=f"db_integrity_{database_path.name}",
            description=f"Check integrity of database {database_path}"
        )
        self.database_path = database_path
        self.integrity_result = None

    def check(self, target: Any) -> bool:
        if not self.database_path.exists():
            return False

        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA integrity_check")
                self.integrity_result = cursor.fetchone()[0]
                return self.integrity_result == 'ok'
        except Exception:
            return False

    def get_failure_message(self, target: Any) -> str:
        if not self.database_path.exists():
            return f"Database {self.database_path} does not exist"
        return f"Database integrity check failed: {self.integrity_result}"


class JsonValidRule(ValidationRule):
    """Rule to check if a file contains valid JSON"""

    def __init__(self, json_file: Path):
        super().__init__(
            name=f"json_valid_{json_file.name}",
            description=f"Check if {json_file} contains valid JSON"
        )
        self.json_file = json_file
        self.error_message = None

    def check(self, target: Any) -> bool:
        if not self.json_file.exists():
            return False

        try:
            with open(self.json_file, 'r') as f:
                json.load(f)
            return True
        except json.JSONDecodeError as e:
            self.error_message = str(e)
            return False
        except Exception as e:
            self.error_message = str(e)
            return False

    def get_failure_message(self, target: Any) -> str:
        if not self.json_file.exists():
            return f"JSON file {self.json_file} does not exist"
        return f"Invalid JSON in {self.json_file}: {self.error_message}"


class ThresholdRule(ValidationRule):
    """Rule to check if a value meets a threshold"""

    def __init__(self, name: str, threshold: float, comparison: str = ">="):
        super().__init__(
            name=name,
            description=f"Check if value {comparison} {threshold}"
        )
        self.threshold = threshold
        self.comparison = comparison
        self.actual_value = None

    def check(self, target: Any) -> bool:
        # Extract numeric value from target
        if isinstance(target, (int, float)):
            self.actual_value = target
        elif isinstance(target, dict) and 'value' in target:
            self.actual_value = target['value']
        else:
            return False

        if self.comparison == ">=":
            return self.actual_value >= self.threshold
        elif self.comparison == "<=":
            return self.actual_value <= self.threshold
        elif self.comparison == ">":
            return self.actual_value > self.threshold
        elif self.comparison == "<":
            return self.actual_value < self.threshold
        elif self.comparison == "==":
            return self.actual_value == self.threshold
        else:
            return False

    def get_failure_message(self, target: Any) -> str:
        return f"Value {self.actual_value} does not meet threshold {self.comparison} {self.threshold}"


class RuleBasedValidator(BaseValidator):
    """Validator that uses a set of rules"""

    def __init__(self, name: str, rules: List[ValidationRule]):
        super().__init__(name)
        self.rules = rules

    def validate(self, target: Any) -> ValidationResult:
        """Validate using all rules"""
        passed_rules = []
        failed_rules = []
        rule_details = {}

        for rule in self.rules:
            try:
                if rule.check(target):
                    passed_rules.append(rule)
                    rule_details[rule.name] = {
                        'status': 'passed',
                        'description': rule.description
                    }
                else:
                    failed_rules.append(rule)
                    rule_details[rule.name] = {
                        'status': 'failed',
                        'description': rule.description,
                        'message': rule.get_failure_message(target)
                    }
            except Exception as e:
                failed_rules.append(rule)
                rule_details[rule.name] = {
                    'status': 'error',
                    'description': rule.description,
                    'error': str(e)
                }

        # Determine overall result
        if failed_rules:
            status = ValidationStatus.FAILED
            message = f"Rule validation failed: {len(failed_rules)}/{len(self.rules)} rules failed"
            errors = [
                rule_details[rule.name].get(
                    'message', f'Rule {rule.name} failed'
                )
                for rule in failed_rules
            ]
        else:
            status = ValidationStatus.PASSED
            message = f"Rule validation passed: {len(passed_rules)}/{len(self.rules)} rules passed"
            errors = []

        return ValidationResult(
            status=status,
            message=message,
            details={
                'rules': rule_details,
                'passed_count': len(passed_rules),
                'failed_count': len(failed_rules)
            },
            errors=errors
        )
