#!/usr/bin/env python3
"""
DatabaseAccessLayer - Enterprise Database Processor
Generated: 2025-07-10 18:09:28

Enterprise Standards Compliance:
- Flake8/PEP 8 Compliant
- Emoji-free code (text-based indicators only)
- Database-first architecture

MODERNIZED: Now uses modular db_tools package for enhanced functionality
while maintaining backward compatibility.
"""

import sys
import logging

# Import from new modular package
from db_tools.operations.access import DatabaseAccessLayer as ModularDatabaseAccessLayer, TEXT_INDICATORS

# For backward compatibility, alias the new class
EnterpriseDatabaseProcessor = ModularDatabaseAccessLayer


def main():
    """Main execution function - maintains backward compatibility"""
    processor = EnterpriseDatabaseProcessor()
    success = processor.execute_processing()

    if success:
        print(f"{TEXT_INDICATORS['success']} Database processing completed")
    else:
        print(f"{TEXT_INDICATORS['error']} Database processing failed")

    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
