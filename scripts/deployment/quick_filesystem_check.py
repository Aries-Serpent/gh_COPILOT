#!/usr/bin/env python3
"""
Quick Filesystem Check Script
"""

import os
import sys

print("FILESYSTEM ISOLATION CHECK")
print("=" * 50)

# Check Python executable
print(f"Python executable: {sys.executable}")

# Check virtual environment
venv = os.environ.get('VIRTUAL_ENV', 'Not set')
print(f"Virtual environment: {venv}")

# Check current directory
print(f"Current directory: {os.getcwd()}")

# Quick C:/Users check
c_users_python_check = "C:\\Users" in sys.executable or "/c/Users" in sys.executable
c_users_venv_check = "C:\\Users" in str(venv) or "/c/Users" in str(venv)
c_users_cwd_check = "C:\\Users" in os.getcwd() or "/c/Users" in os.getcwd()

print("\nVIOLATION CHECK:")
print(f"Python in C:/Users: {c_users_python_check}")
print(f"Venv in C:/Users: {c_users_venv_check}")
print(f"CWD in C:/Users: {c_users_cwd_check}")

violations = c_users_python_check or c_users_venv_check or c_users_cwd_check

if violations:
    print("\n[ERROR] VIOLATIONS DETECTED")
else:
    print("\n[SUCCESS] NO VIOLATIONS - FILESYSTEM ISOLATION COMPLIANT")

# Save quick results
with open('quick_filesystem_check.txt', 'w') as f:
    f.write(f"Python: {sys.executable}\n")
    f.write(f"Venv: {venv}\n")
    f.write(f"CWD: {os.getcwd()}\n")
    f.write(f"Violations: {violations}\n")

print(
f"\nResults saved to: {os.path.join(os.getcwd(), 'quick_filesystem_check.txt')}")
