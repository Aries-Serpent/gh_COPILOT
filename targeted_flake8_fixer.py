#!/usr/bin/env python3
"""
🛠️ TARGETED FLAKE8 COMPLIANCE FIXER
==================================
Systematic fix for specific files with comprehensive error handling
"""

import os
import re
import subprocess
from pathlib import Path

def fix_line_length_violations():
    """Fix E501 violations by intelligently wrapping lines"""

    files_to_fix = []

    for filename in files_to_fix:
        if not Path(filename).exists():
            continue

        print(f"🔧 Fixing line length in {filename}")

        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()

        lines = content.split('\n')
        fixed_lines = []

        for line in lines:
            if len(line) > 79:
                # Handle imports
                if line.strip().startswith('from ') and ' import ' in line:
                    if ',' in line:
                        parts = line.split(' import ', 1)
                        from_part = parts[0]
                        imports = [imp.strip() for imp in parts[1].split(',')]

                        if len(imports) > 1:
                            fixed_lines.append(f"{from_part} import (")
                            for i, imp in enumerate(imports):
                                if i == len(imports) - 1:
                                    fixed_lines.append(f"    {imp}")
                                else:
                                    fixed_lines.append(f"    {imp},")
                            fixed_lines.append(")")
                            continue

                # Handle long strings - simple break at 70 chars
                if '"' in line and len(line) > 79:
                    indent = len(line) - len(line.lstrip())
                    if 'f"' in line or '"' in line:
                        # Simple approach: break at logical points
                        break_point = line.rfind(' ', 0, 75)
                        if break_point > 50:
                            line1 = line[:break_point] + " \\"
                            line2 = ' ' * (indent + 4) + line[break_point:].lstrip()
                            fixed_lines.append(line1)
                            fixed_lines.append(line2)
                            continue

            fixed_lines.append(line)

        # Write back if changed
        new_content = '\n'.join(fixed_lines)
        if new_content != content:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"✅ Fixed line lengths in {filename}")

def remove_unused_imports():
    """Remove F401 unused import violations"""
    # Use autopep8 to remove unused imports
    try:
        subprocess.run(
            [
                'python', '-m', 'autopep8',
                '--in-place', '--aggressive', '--aggressive',
                '--remove-all-unused-imports',
                '--recursive', '.'
            ],
            check=True,
            cwd='.'
        )
        print("✅ Removed unused imports")
    except Exception as e:
        print(f"❌ Error removing unused imports: {e}")

def fix_whitespace_issues():
    """Fix W293 and W291 whitespace violations"""

    python_files = list(Path('.').glob('*.py'))

    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Fix trailing whitespace and whitespace-only lines
            lines = content.split('\n')
            fixed_lines = []

            for line in lines:
                # Remove trailing whitespace
                line = line.rstrip()
                fixed_lines.append(line)

            new_content = '\n'.join(fixed_lines)

            if new_content != content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"✅ Fixed whitespace in {file_path}")

        except Exception as e:
            print(f"❌ Error fixing {file_path}: {e}")

def fix_fstring_violations():
    """Fix F541 f-string without placeholders"""

    python_files = list(Path('.').glob('*.py'))

    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Find f-strings without placeholders and convert to regular strings
            # Pattern: f"text without {placeholders}"
            pattern = r'f"([^"]*)"'

            def replace_fstring(match):
                string_content = match.group(1)
                if '{' not in string_content and '}' not in string_content:
                    return f'"{string_content}"'
                return match.group(0)

            new_content = re.sub(pattern, replace_fstring, content)

            if new_content != content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"✅ Fixed f-strings in {file_path}")

        except Exception as e:
            print(f"❌ Error fixing f-strings in {file_path}: {e}")

def run_targeted_fixes():
    """Run all targeted fixes"""
    print("🚀 Starting targeted Flake8 compliance fixes...")

    # Step 1: Fix whitespace issues (easiest)
    print("\n📝 Step 1: Fixing whitespace issues...")
    fix_whitespace_issues()

    # Step 2: Fix f-string violations
    print("\n🔤 Step 2: Fixing f-string violations...")
    fix_fstring_violations()

    # Step 3: Remove unused imports
    print("\n📦 Step 3: Removing unused imports...")
    remove_unused_imports()

    # Step 4: Fix line length violations
    print("\n📏 Step 4: Fixing line length violations...")
    fix_line_length_violations()

    # Step 5: Check remaining violations
    print("\n🔍 Step 5: Checking remaining violations...")
    try:
        result = subprocess.run(
            [
                'flake8',
                '--format=%(path)s:%(row)d:%(col)d:%(code)s:%(text)s',
                '--max-line-length=88',
                '--ignore=E203,W503',
                '.'
            ],
            capture_output=True, text=True, cwd='.'
        )

        print("📊 Remaining violations:")
        print(result.stdout)

        if result.returncode == 0:
            print("✅ ALL VIOLATIONS FIXED! 🎉")
        else:
            print("⚠️ Some violations remain - may need manual review")
    except Exception as e:
        print(f"❌ Error running flake8: {e}")

if __name__ == "__main__":
    run_targeted_fixes()
