"""
Validation Package

Unified validation utilities for the gh_COPILOT toolkit.
Provides modular session validation, deployment validation, and compliance checking.
"""

__version__ = "1.0.0"

# Import main classes for easy access
from .core.validators import BaseValidator, ValidationResult
from .protocols.session import SessionProtocolValidator
from .protocols.deployment import DeploymentValidator
from .reporting.formatters import ValidationReportFormatter

__all__ = [
    "BaseValidator",
    "ValidationResult",
    "SessionProtocolValidator",
    "DeploymentValidator",
    "ValidationReportFormatter",
]
