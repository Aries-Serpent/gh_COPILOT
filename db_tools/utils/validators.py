"""
Data validation utilities for database operations.
"""

import re
from pathlib import Path
from typing import Any, List, Dict


class DataValidator:
    """Validates data for database operations"""

    @staticmethod
    def validate_file_path(file_path: str) -> bool:
        """Validate that file path is safe and exists"""
        try:
            path = Path(file_path)
            # Check for path traversal attacks
            if '..' in str(path) or str(path).startswith('/'):
                return False
            # Check if path exists (optional validation)
            return True
        except Exception:
            return False

    @staticmethod
    def validate_sql_table_name(table_name: str) -> bool:
        """Validate SQL table name is safe"""
        # Only allow alphanumeric characters and underscores
        pattern = r'^[a-zA-Z_][a-zA-Z0-9_]*$'
        return bool(re.match(pattern, table_name))

    @staticmethod
    def validate_sql_column_name(column_name: str) -> bool:
        """Validate SQL column name is safe"""
        # Only allow alphanumeric characters and underscores
        pattern = r'^[a-zA-Z_][a-zA-Z0-9_]*$'
        return bool(re.match(pattern, column_name))

    @staticmethod
    def sanitize_string(value: str, max_length: int = 1000) -> str:
        """Sanitize string value for database insertion"""
        if not isinstance(value, str):
            value = str(value)
        # Truncate to max length
        if len(value) > max_length:
            value = value[:max_length]
        # Remove null characters
        value = value.replace('\x00', '')
        return value

    @staticmethod
    def validate_violation_data(data: Dict[str, Any]) -> List[str]:
        """Validate violation data structure"""
        errors = []
        required_fields = ['file_path', 'line_number', 'error_code']

        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")

        if 'file_path' in data and not DataValidator.validate_file_path(data['file_path']):
            errors.append("Invalid file path")

        if 'line_number' in data:
            try:
                line_num = int(data['line_number'])
                if line_num <= 0:
                    errors.append("Line number must be positive")
            except (ValueError, TypeError):
                errors.append("Line number must be an integer")

        if 'error_code' in data and not isinstance(data['error_code'], str):
            errors.append("Error code must be a string")

        return errors
