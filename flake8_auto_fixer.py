#!/usr/bin/env python3
"""
AUTOMATED FLAKE8 COMPLIANCE FIXER
=================================
Fixes common Flake8 issues automatically.
"""

import re
import sys



def fix_flake8_issues(file_path: str):
    """Fix common Flake8 issues in a Python file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # Fix W293 - blank line contains whitespace
    content = re.sub(r'^[ \t]+$', '', content, flags=re.MULTILINE)

    # Fix W291 - trailing whitespace
    content = re.sub(r'[ \t]+$', '', content, flags=re.MULTILINE)

    # Fix E501 - line too long (split long lines at appropriate points)
    lines = content.split('\n')
    fixed_lines = []

    for line in lines:
        if len(line) > 100:
            # Try to split at common break points
            if ' and ' in line and len(line) > 100:
                parts = line.split(' and ')
                if len(parts) == 2:
                    indent = len(line) - len(line.lstrip())
                    line = parts[0] + ' and \\\n' + ' ' * (indent + 4) + parts[1]
            elif ', ' in line and len(line) > 100:
                # Split at comma if line is too long
                parts = line.split(', ')
                if len(parts) > 2:
                    indent = len(line) - len(line.lstrip())
                    new_line = parts[0]
                    for part in parts[1:]:
                        if len(new_line + ', ' + part) > 100:
                            new_line += ',\n' + ' ' * (indent + 4) + part
                        else:
                            new_line += ', ' + part
                    line = new_line

        fixed_lines.append(line)

    content = '\n'.join(fixed_lines)

    # Remove unused imports (common ones)
    unused_imports = [
        'import os\n',
        'from concurrent.futures import ThreadPoolExecutor, as_completed\n',
        'import shutil\n',
        'import flask\n',
        'from flask import render_template, request\n'
    ]

    for unused in unused_imports:
        if unused in content and not re.search(
                                               rf'\b{unused.split()[-1].replace(",",
                                               "").replace("ThreadPoolExecutor",
                                               "ThreadPoolExecutor|as_completed")}\b',
                                               content.replace(unused,
                                               ''))
        if unused in content and not re.search(rf'\b{u)
            content = content.replace(unused, '')

    # Fix F541 - f-string missing placeholders
    content = re.sub(r'f"([^{]*)"', r'"\1"', content)
    content = re.sub(r"f'([^{]*)'", r"'\1'", content)

    # Remove unused variables (F841)
    content = re.sub(r'\n\s*backup_path = [^\n]*\n', '\n', content)

    # Write back only if changes were made
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed Flake8 issues in {file_path}")
        return True
    else:
        print(f"No Flake8 issues to fix in {file_path}")
        return False


if __name__ == "__main__":
    file_path = sys.argv[1] if len(sys.argv) > 1 else "comprehensive_pis_framework.py"
    fix_flake8_issues(file_path)
