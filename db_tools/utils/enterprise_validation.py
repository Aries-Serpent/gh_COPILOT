"""Deprecated validation helpers.

This module now re-exports :func:`enterprise_modules.compliance.validate_enterprise_operation`
for backward compatibility.
"""

from enterprise_modules.compliance import validate_enterprise_operation

__all__ = ["validate_enterprise_operation"]
