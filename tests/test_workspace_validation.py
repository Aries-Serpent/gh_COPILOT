#!/usr/bin/env python3
"""Unit tests for enhanced workspace validation."""

import unittest
from unittest.mock import patch


class TestWorkspaceValidation(unittest.TestCase):
    """Test enhanced workspace validation functionality."""

    def test_proper_root_validation_compliant(self):
        """Workspace validation should pass with compliant path."""
        with patch("os.getcwd", return_value="/path/to/gh_COPILOT"):
            from enterprise_modules.compliance import validate_enterprise_operation

            result = validate_enterprise_operation()
            self.assertTrue(result)

    def test_proper_root_validation_non_compliant(self):
        """Non-compliant path should return False with warning."""
        with patch("os.getcwd", return_value="/some/random/path"):
            from enterprise_modules.compliance import validate_enterprise_operation

            result = validate_enterprise_operation()
            self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
