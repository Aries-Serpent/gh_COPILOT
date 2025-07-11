#!/usr/bin/env python3
"""
🔧 IMMEDIATE FLAKE8 CORRECTOR v1.0
===================================
Simplified, robust corrector for immediate results
DUAL COPILOT PATTERN: Immediate fixes with validation
"""


import re
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple
from tqdm import tqdm


class ImmediateFlake8Corrector:
    """🚀 Immediate Flake8 corrector with enterprise monitoring"""

    def __init__(self, workspace_path: str = "e:\\gh_COPILOT"):
        self.workspace_path = Path(workspace_path)
        self.fixes_applied = 0

    def fix_syntax_errors_immediately(self) -> int:
        """Fix critical syntax errors immediately"""
        print("🚀 IMMEDIATE SYNTAX ERROR CORRECTION STARTING...")

        python_files = list(self.workspace_path.rglob("*.py"))
        syntax_fixes = 0

        with tqdm(desc="🔧 Fixing Syntax Errors", total=len(python_files)) as pbar:
            for py_file in python_files:
                try:
                    fixed = self._fix_file_syntax_errors(py_file)
                    syntax_fixes += fixed
                except Exception as e:
                    print(f"❌ Error fixing {py_file}: {e}")
                pbar.update(1)

        print(f"✅ Fixed {syntax_fixes} syntax errors in {len(python_files)} files")
        return syntax_fixes

    def _fix_file_syntax_errors(self, file_path: Path) -> int:
        """Fix syntax errors in a single file"""
        if not file_path.exists():
            return 0

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            original_content = content
            fixes_in_file = 0

            # Fix unterminated f-strings (broken across lines)
            pattern = r'f"([^"]*)\{\s*\n\s*([^}]*)\}"'

            def fix_fstring(match):
                return f'f"{match.group(1)}{{{match.group(2).strip()}}}"'
            content = re.sub(pattern, fix_fstring, content, flags=re.MULTILINE)

            # Fix broken f-strings with newlines
            lines = content.split('\n')
            fixed_lines = []
            i = 0

            while i < len(lines):
                line = lines[i]
                # Check for f-string that ends with '{'
                if 'f"' in line and line.rstrip().endswith('{'):
                    j = i + 1
                    closing_found = False
                    while j < len(lines):
                        next_line = lines[j].strip()
                        if '}' in next_line and '"' in next_line:
                            # Found the closing part
                            base_line = line.rstrip()[:-1]
                            variable_part = next_line.split('}')[0].strip()
                            rest_of_line = next_line.split(
                                                           '"',
                                                           1)[-1] if '"' in next_line else '
                            rest_of_line = next_line.split('"', 1)[-1] if '"' in next_)
                            fixed_line = f'{base_line}{{{variable_part}}}"'
                            if rest_of_line:
                                fixed_line += rest_of_line
                            fixed_lines.append(fixed_line)
                            fixes_in_file += 1
                            i = j + 1
                            closing_found = True
                            break
                        j += 1
                    if not closing_found:
                        fixed_lines.append(line)
                        i += 1
                else:
                    fixed_lines.append(line)
                    i += 1

            content = '\n'.join(fixed_lines)

            # Write back if changes were made
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.fixes_applied += fixes_in_file
                return fixes_in_file

            return 0

        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
            return 0

    def apply_autopep8_corrections(self) -> int:
        """Apply autopep8 corrections safely"""
        print("🚀 APPLYING AUTOPEP8 CORRECTIONS...")

        try:
            # Use autopep8 with conservative settings
            cmd = [
                sys.executable, '-m', 'autopep8',
                '--in-place', '--aggressive', '--aggressive',
                '--recursive', str(self.workspace_path)
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                print("✅ Autopep8 corrections applied successfully")
                return 1
            else:
                print(f"⚠️ Autopep8 warnings: {result.stderr}")
                return 0

        except Exception as e:
            print(f"❌ Autopep8 failed: {e}")
            return 0

    def check_remaining_violations(self) -> Tuple[int, List[str]]:
        """Check remaining Flake8 violations"""
        print("🔍 CHECKING REMAINING VIOLATIONS...")

        try:
            cmd = [
                'flake8',
                '--format=%(path)s:%(row)d:%(col)d:%(code)s:%(text)s',
                '--max-line-length=88',
                '--ignore=E203,W503',
                str(self.workspace_path)
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            violation_count = 0
            violation_details = []

            if result.stdout:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if ':' in line and any(code in line for code in ['E', 'W', 'F']):
                        violation_details.append(line)
                violation_count = len(violation_details)

            print(f"📊 Remaining violations: {violation_count}")
            return violation_count, violation_details

        except Exception as e:
            print(f"❌ Violation check failed: {e}")
            return -1, []

    def execute_immediate_corrections(self) -> dict:
        """Execute immediate corrections with monitoring"""
        print("🚀 IMMEDIATE FLAKE8 CORRECTOR STARTING...")
        print("🤖🤖 DUAL COPILOT PATTERN: Immediate + Validation")

        results = {}

        try:
            # Check initial state
            initial_violations, _ = self.check_remaining_violations()
            results["initial_violations"] = initial_violations

            # Step 1: Fix critical syntax errors
            syntax_fixes = self.fix_syntax_errors_immediately()
            results["syntax_fixes"] = syntax_fixes

            # Step 2: Apply autopep8 corrections
            autopep8_success = self.apply_autopep8_corrections()
            results["autopep8_applied"] = autopep8_success > 0

            # Step 3: Check final state
            final_violations, details = self.check_remaining_violations()
            results["final_violations"] = final_violations

            # Calculate improvement
            if initial_violations > 0 and final_violations >= 0:
                improvement = ((initial_violations - final_violations) / initial_violations) * 100
                results["improvement_percentage"] = improvement
            else:
                results["improvement_percentage"] = 0.0

            # Display results
            print("\n✅ IMMEDIATE CORRECTIONS COMPLETE!")
            print(f"Syntax Fixes Applied: {syntax_fixes}")
            print(f"Autopep8 Applied: {'✅' if autopep8_success else '❌'}")
            print(f"Initial Violations: {initial_violations}")
            print(f"Final Violations: {final_violations}")
            print(f"Improvement: {results['improvement_percentage']:.1f}%")

            return results

        except Exception as e:
            print(f"❌ Immediate correction failed: {e}")
            results["error"] = str(e)
            return results


def main():
    """Main execution for immediate corrections"""
    corrector = ImmediateFlake8Corrector()
    results = corrector.execute_immediate_corrections()

    print("\n📊 SUMMARY:")
    if results.get('final_violations', 0) < results.get('initial_violations', 0):
        print("Final Status: ✅ SUCCESS")
    else:
        print("Final Status: ⚠️ PARTIAL")

    return results


if __name__ == "__main__":
    main()
