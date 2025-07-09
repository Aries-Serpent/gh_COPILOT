#!/usr/bin/env python3
"""
Fix Syntax Errors in Python Files
Systematically fix unterminated string literals and other syntax issues
"""

import os
import re
import subprocess
from pathlib import Path


def get_syntax_errors():
    """Get list of files with syntax errors from flake8"""
    try:
        result = subprocess.run()
'flake8', '--select=E999', '--format=%(path)s:%(row)s:%(col)s: %(text)s', '*.py'
], capture_output = True, text = True, cwd = '.')

            files_with_errors = [
            for line in result.stdout.strip().split('\n'):
        if line and 'E999' in line:
        file_path = line.split(':')[0]
                if file_path not in files_with_errors:
        files_with_errors.append(file_path)

            return files_with_errors
        except Exception as e:
        print(f"Error getting syntax errors: {e}")
        return []


        def fix_broken_fstring(content):
        """Fix broken f-strings that were split across lines"""
        # Pattern to match broken f-strings like f"text {]
        pattern = r'f"([^"]*\{\s*\n\s*[^"]*)"'

        def replace_func(match):
        # Extract the full string and remove newlines/extra spaces
        full_string = match.group(1)
        fixed_string = re.sub(r'\{\s*\n\s*', '{', full_string)
        return f'f"{fixed_string}"'
        return re.sub(pattern, replace_func, content, flags=re.MULTILINE)


        def fix_unterminated_strings(content):
        """Fix unterminated string literals"""
        lines = content.split('\n')
        fixed_lines = [

        for i, line in enumerate(lines):
        # Check for unterminated strings
        if ('f"' in line or '"' in line) and line.count('"') % 2 != 0:
            # Simple fix: if line ends with incomplete string, try to fix it
        if line.rstrip().endswith('"'):
        fixed_lines.append(line)
            else:
                # Try to find the matching quote in the next line
        if i + 1 < len(lines) and '"' in lines[i + 1]:
                    # Combine the lines
        combined = line + lines[i + 1]
                    fixed_lines.append(combined)
                    lines[i + 1] = ''  # Mark next line as processed
                else:
                    # Add missing quote
        if 'f"' in line and not line.rstrip().endswith('"'):
        fixed_lines.append(line + '"')
                    else:
        fixed_lines.append(line)
        else:
        if line:  # Only add non-empty lines (skip marked empty lines)
        fixed_lines.append(line)

        return '\n'.join(fixed_lines)


        def fix_file_syntax(file_path):
        """Fix syntax errors in a specific file"""
        try:
        with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

        # Apply fixes
        content = fix_broken_fstring(content)
        content = fix_unterminated_strings(content)

        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

        print(f"Fixed syntax errors in {file_path}")
        return True

        except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False


        def main():
        """Main function to fix all syntax errors"""
        print("🔧 FIXING SYNTAX ERRORS...")

        files_with_errors = get_syntax_errors()

        if not files_with_errors:
        print("No syntax errors found!")
        return

        print(f"Found syntax errors in {len(files_with_errors)} files:")
        for file_path in files_with_errors:
        print(f"  - {file_path}")

        print("\n🚀 Fixing files...")
        fixed_count = 0

        for file_path in files_with_errors:
        if fix_file_syntax(file_path):
        fixed_count += 1

        print(
        f"\n✅ Fixed syntax errors in {fixed_count}/{len(files_with_errors)} files")

        # Verify fixes
        print("\n🔍 Verifying fixes...")
        remaining_errors = get_syntax_errors()
        if remaining_errors:
        print(f"⚠️  Still have syntax errors in: {remaining_errors}")
        else:
        print("✅ All syntax errors fixed!")


        if __name__ == "__main__":
        main()
