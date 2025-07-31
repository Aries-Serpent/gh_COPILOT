#!/usr/bin/env python3
"""
SessionProtocolValidator - Validates workspace for zero-byte files.

MODERNIZED: Now uses modular validation package for enhanced functionality
while maintaining backward compatibility.
"""

import sys

# Import from new modular package
from validation.protocols.session import main

# This script now delegates to the modular implementation
if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
