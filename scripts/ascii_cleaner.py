#!/usr/bin/env python3
"""
Simple ASCII-Only Cleaner for Enterprise Compliance
===================================================

This script removes ALL non-ASCII characters from Python files to ensure
100% enterprise compliance with professional logging standards.
"""

import os
import sys
import re
import shutil
from datetime import datetime
from pathlib import Path


def clean_file_to_ascii(file_path: str) -> tuple:
    """Clean a file to contain only ASCII characters."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Count non-ASCII characters
        non_ascii_count = len([c for c in content if ord(c) > 127])

        if non_ascii_count == 0:
            return False, 0  # No changes needed

        # Remove all non-ASCII characters
        ascii_content = ''.join(c if ord(c) <= 127 else '' for c in content)

        # Create backup
        backup_path = file_path + '.backup'
        shutil.copy2(file_path, backup_path)

        # Write clean content
        with open(file_path, 'w', encoding='ascii', errors='ignore') as f:
            f.write(ascii_content)

        return True, non_ascii_count

    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        return False, 0


def main():
    base_path = Path("E:/gh_COPILOT")
    print(f"Cleaning all Python files in {base_path}")

    total_files = 0
    modified_files = 0
    total_chars_removed = 0

    for py_file in base_path.glob("*.py"):
        total_files += 1
        modified, chars_removed = clean_file_to_ascii(str(py_file))

        if modified:
            modified_files += 1
            total_chars_removed += chars_removed
            print(
             f"Cleaned {py_file.name}: removed {chars_removed} non-ASCII characters")

                  print(
                  f"\\nComplete: {total_files} files processed, {modified_files} modified")
                  print(f"Total non-ASCII characters removed: {total_chars_removed}")

                  # Validate all files are now ASCII-only
                  validation_passed = True
                  for py_file in base_path.glob("*.py"):
                   try:
                  with open(py_file, 'r', encoding='ascii') as f:
                f.read()
                  except UnicodeDecodeError:
                  print(
                f"WARNING: {py_file.name} still contains non-ASCII characters")
                  validation_passed = False

                  if validation_passed:
                  print("SUCCESS: All files are now ASCII-only and enterprise compliant!")
                  return 0
                  else:
                  print("WARNING: Some files may still contain non-ASCII characters")
                  return 1


                  if __name__ == "__main__":
                  sys.exit(main())
