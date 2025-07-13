#!/usr/bin/env python3
"""
🚀 PHASE 4 SYSTEMATIC PROCESSOR - FIXED VERSION
Enterprise-Grade High-Impact Violation Elimination System

CRITICAL FIX: Corrected file path handling bug that caused 0% success rate
TARGET: 1,159 high-impact violations across 4 categories
SUCCESS PROJECTION: 92%+ elimination rate (1,066+ violations fixed)
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
from tqdm import tqdm
import logging
import re

# Enterprise logging setup with encoding fix
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('phase4_systematic_processing_fixed.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class Phase4Metrics:
    """📊 Phase 4 Processing Metrics"""
    start_time: datetime = field(default_factory=datetime.now)
    end_time: datetime = None
    target_violations: int = 1159
    total_violations: int = 0
    violations_fixed: int = 0
    categories_processed: int = 0
    files_modified: int = 0
    processing_errors: List[str] = field(default_factory=list)
    success_rate: float = 0.0

    def calculate_success_rate(self):
        """Calculate overall success rate"""
        if self.target_violations > 0:
            self.success_rate = (self.violations_fixed / self.target_violations) * 100
        return self.success_rate


class Phase4SystematicProcessorFixed:
    """🚀 Phase 4 Systematic Processor - FIXED VERSION"""

    def __init__(self, workspace_path: str = "e:/gh_COPILOT"):
        self.workspace_path = Path(workspace_path)
        self.metrics = Phase4Metrics()

        # Enterprise violation categories with projections
        self.target_categories = {
            "E305": {
        "count": 518,
        "description": "Expected 2 blank lines after class/function definition",
        "difficulty": "LOW",
        "success_rate": 95},
            "E303": {
        "count": 496,
        "description": "Too many blank lines",
        "difficulty": "LOW",
        "success_rate": 95},
            "W291": {
        "count": 88,
        "description": "Trailing whitespace",
        "difficulty": "LOW",
        "success_rate": 99},
            "F541": {
        "count": 57,
        "description": "f-string missing placeholders",
        "difficulty": "LOW",
        "success_rate": 90}
        }

        # MANDATORY: Enterprise initialization
        logger.info("="*80)
        logger.info("🚀 PHASE 4 SYSTEMATIC PROCESSOR - FIXED VERSION INITIALIZED")
        logger.info("Mission: High-Impact Violation Elimination")
        logger.info(f"Target Violations: {self.metrics.target_violations:,}")
        logger.info(f"Start Time: {self.metrics.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Process ID: {os.getpid()}")
        logger.info(f"Workspace: {self.workspace_path}")
        logger.info("="*80)

    def run_baseline_scan(self) -> Dict[str, int]:
        """🔍 Execute baseline violation scan"""
        logger.info("🔍 PHASE 4 BASELINE SCANNING INITIATED...")

        baseline_counts = {}

        with tqdm(total=100, desc="🔄 Baseline Scan", unit="%",
                 bar_format="{l_bar}{bar}| {n:.1f}/{total}{unit} [{elapsed}<{remaining}]") as pbar:

            for i, (code, info) in enumerate(self.target_categories.items()):
                pbar.set_description(f"🔍 Scanning {code}")

                try:
                    result = subprocess.run(
                        ['python', '-m', 'flake8', f'--select={code}', '.'],
                        capture_output=True, text=True, encoding='utf-8', cwd=self.workspace_path
                    )

                    violations = self._parse_flake8_output(result.stdout)
                    baseline_counts[code] = len(violations)

                    logger.info(f"  {code}: {len(violations):3d} violations - {info['description']}")
                    logger.info(f"       Difficulty: {info['difficulty']:4s} | Success: {info['success_rate']}%")

                except subprocess.CalledProcessError as e:
                    logger.error(f"Failed to scan {code}: {e}")
                    baseline_counts[code] = 0

                pbar.update(25)

        self.metrics.total_violations = sum(baseline_counts.values())
        logger.info(f"📊 BASELINE TOTAL: {self.metrics.total_violations:,} violations")

        return baseline_counts

    def process_phase4_categories(self) -> Dict[str, Dict[str, Any]]:
        """🎯 Process all Phase 4 violation categories"""
        logger.info("🎯 PHASE 4 CATEGORY PROCESSING INITIATED...")

        category_results = {}

        with tqdm(
            total=len(self.target_categories),
            desc="🔄 Processing Categories",
            unit="category") as pbar:

            for code, info in self.target_categories.items():
                pbar.set_description(f"🔧 Processing {code}")

                logger.info(f"🎯 Processing {code}: {info['description']}")
                logger.info(f"   Target: {info['count']} violations - {info['description']}")

                start_time = datetime.now()

                # Execute category-specific processing
                if code == "E305":
                    fixes_made = self._fix_e305_blank_lines_after_function(code)
                elif code == "E303":
                    fixes_made = self._fix_e303_too_many_blank_lines(code)
                elif code == "W291":
                    fixes_made = self._fix_w291_trailing_whitespace(code)
                elif code == "F541":
                    fixes_made = self._fix_f541_fstring_placeholders(code)
                else:
                    fixes_made = 0

                duration = (datetime.now() - start_time).total_seconds()

                category_results[code] = {
                    "fixes_made": fixes_made,
                    "duration": duration,
                    "target_count": info['count'],
                    "success_rate": (fixes_made / info['count'] * 100) if info['count'] > 0 else 0
                }

                self.metrics.violations_fixed += fixes_made
                self.metrics.categories_processed += 1

                logger.info(f"✅ {code} Processing Complete: {fixes_made} fixes in {duration:.1f}s")
                pbar.update(1)

        return category_results

    def _fix_e305_blank_lines_after_function(self, violation_code: str) -> int:
        """Fix E305: Expected 2 blank lines after class or function definition"""
        fixes_made = 0

        try:
            result = subprocess.run(
                ['python', '-m', 'flake8', '--select=E305', '.'],
                capture_output=True, text=True, encoding='utf-8', cwd=self.workspace_path
            )

            violations = self._parse_flake8_output(result.stdout)

            with tqdm(total=len(violations), desc=f"🔧 Fixing {violation_code}", unit="fix") as pbar:
                for file_path, line_num, col, msg in violations:
                    try:
                        if self._fix_single_e305(file_path, line_num):
                            fixes_made += 1
                        pbar.update(1)
                    except Exception as e:
                        logger.warning(f"Failed to fix E305 in {file_path}:{line_num}: {e}")

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get E305 violations: {e}")

        return fixes_made

    def _fix_single_e305(self, file_path: str, line_num: int) -> bool:
        """Fix single E305 violation by adding blank lines"""
        try:
            # CRITICAL FIX: Properly construct file path
            if file_path.startswith('./'):
                file_path = file_path[2:]  # Remove './'
            elif file_path.startswith('.\\'):
                file_path = file_path[2:]  # Remove '.\\'
            elif file_path.startswith('\\'):
                file_path = file_path[1:]  # Remove leading backslash

            full_path = self.workspace_path / file_path

            if not full_path.exists():
                logger.warning(f"File not found: {full_path}")
                return False

            with open(full_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Add blank lines after function/class definition
            if line_num > 1 and line_num <= len(lines):
                # Find the end of the function/class definition
                insert_pos = line_num - 1  # Convert to 0-based

                # Count existing blank lines before this line
                blank_count = 0
                for i in range(insert_pos - 1, -1, -1):
                    if i < 0 or lines[i].strip():
                        break
                    blank_count += 1

                # Add blank lines if needed (target is 2)
                lines_to_add = max(0, 2 - blank_count)
                if lines_to_add > 0:
                    for _ in range(lines_to_add):
                        lines.insert(insert_pos, '\n')

                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.writelines(lines)
                    return True

        except Exception as e:
            logger.warning(f"Error fixing E305 in {file_path}: {e}")

        return False

    def _fix_e303_too_many_blank_lines(self, violation_code: str) -> int:
        """Fix E303: Too many blank lines"""
        fixes_made = 0

        try:
            result = subprocess.run(
                ['python', '-m', 'flake8', '--select=E303', '.'],
                capture_output=True, text=True, encoding='utf-8', cwd=self.workspace_path
            )

            violations = self._parse_flake8_output(result.stdout)

            with tqdm(total=len(violations), desc=f"🔧 Fixing {violation_code}", unit="fix") as pbar:
                for file_path, line_num, col, msg in violations:
                    try:
                        if self._fix_single_e303(file_path, line_num):
                            fixes_made += 1
                        pbar.update(1)
                    except Exception as e:
                        logger.warning(f"Failed to fix E303 in {file_path}:{line_num}: {e}")

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get E303 violations: {e}")

        return fixes_made

    def _fix_single_e303(self, file_path: str, line_num: int) -> bool:
        """Fix single E303 violation by removing excess blank lines"""
        try:
            # CRITICAL FIX: Properly construct file path
            if file_path.startswith('./'):
                file_path = file_path[2:]
            elif file_path.startswith('.\\'):
                file_path = file_path[2:]
            elif file_path.startswith('\\'):
                file_path = file_path[1:]

            full_path = self.workspace_path / file_path

            if not full_path.exists():
                logger.warning(f"File not found: {full_path}")
                return False

            with open(full_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Remove excess blank lines
            if line_num > 0 and line_num <= len(lines):
                line_idx = line_num - 1  # Convert to 0-based

                # Remove consecutive blank lines above, keeping only 2
                removed_lines = 0
                i = line_idx - 1
                while i >= 0 and not lines[i].strip():
                    if removed_lines >= 2:  # Keep only 2 blank lines
                        lines.pop(i)
                        removed_lines += 1
                    else:
                        removed_lines += 1
                    i -= 1

                if removed_lines > 2:
                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.writelines(lines)
                    return True

        except Exception as e:
            logger.warning(f"Error fixing E303 in {file_path}: {e}")

        return False

    def _fix_w291_trailing_whitespace(self, violation_code: str) -> int:
        """Fix W291: Trailing whitespace"""
        fixes_made = 0

        try:
            result = subprocess.run(
                ['python', '-m', 'flake8', '--select=W291', '.'],
                capture_output=True, text=True, encoding='utf-8', cwd=self.workspace_path
            )

            violations = self._parse_flake8_output(result.stdout)

            with tqdm(total=len(violations), desc=f"🔧 Fixing {violation_code}", unit="fix") as pbar:
                for file_path, line_num, col, msg in violations:
                    try:
                        if self._fix_single_w291(file_path, line_num):
                            fixes_made += 1
                        pbar.update(1)
                    except Exception as e:
                        logger.warning(f"Failed to fix W291 in {file_path}:{line_num}: {e}")

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get W291 violations: {e}")

        return fixes_made

    def _fix_single_w291(self, file_path: str, line_num: int) -> bool:
        """Fix single W291 violation by removing trailing whitespace"""
        try:
            # CRITICAL FIX: Properly construct file path
            if file_path.startswith('./'):
                file_path = file_path[2:]
            elif file_path.startswith('.\\'):
                file_path = file_path[2:]
            elif file_path.startswith('\\'):
                file_path = file_path[1:]

            full_path = self.workspace_path / file_path

            if not full_path.exists():
                logger.warning(f"File not found: {full_path}")
                return False

            with open(full_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Remove trailing whitespace from the specified line
            if line_num > 0 and line_num <= len(lines):
                line_idx = line_num - 1  # Convert to 0-based
                original_line = lines[line_idx]
                cleaned_line = original_line.rstrip() + '\n' if original_line.endswith('\n') else original_line.rstrip()

                if original_line != cleaned_line:
                    lines[line_idx] = cleaned_line

                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.writelines(lines)
                    return True

        except Exception as e:
            logger.warning(f"Error fixing W291 in {file_path}: {e}")

        return False

    def _fix_f541_fstring_placeholders(self, violation_code: str) -> int:
        """Fix F541: f-string is missing placeholders"""
        fixes_made = 0

        try:
            result = subprocess.run(
                ['python', '-m', 'flake8', '--select=F541', '.'],
                capture_output=True, text=True, encoding='utf-8', cwd=self.workspace_path
            )

            violations = self._parse_flake8_output(result.stdout)

            with tqdm(total=len(violations), desc=f"🔧 Fixing {violation_code}", unit="fix") as pbar:
                for file_path, line_num, col, msg in violations:
                    try:
                        if self._fix_single_f541(file_path, line_num):
                            fixes_made += 1
                        pbar.update(1)
                    except Exception as e:
                        logger.warning(f"Failed to fix F541 in {file_path}:{line_num}: {e}")

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get F541 violations: {e}")

        return fixes_made

    def _fix_single_f541(self, file_path: str, line_num: int) -> bool:
        """Fix single F541 violation by converting f-string to regular string"""
        try:
            # CRITICAL FIX: Properly construct file path
            if file_path.startswith('./'):
                file_path = file_path[2:]
            elif file_path.startswith('.\\'):
                file_path = file_path[2:]
            elif file_path.startswith('\\'):
                file_path = file_path[1:]

            full_path = self.workspace_path / file_path

            if not full_path.exists():
                logger.warning(f"File not found: {full_path}")
                return False

            with open(full_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Fix f-string without placeholders
            if line_num > 0 and line_num <= len(lines):
                line_idx = line_num - 1  # Convert to 0-based
                original_line = lines[line_idx]

                # Replace f"..." or f'...' with regular strings if no placeholders
                fixed_line = re.sub(r'f(["\'])([^{]*?)\1', r'\1\2\1', original_line)

                if original_line != fixed_line:
                    lines[line_idx] = fixed_line

                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.writelines(lines)
                    return True

        except Exception as e:
            logger.warning(f"Error fixing F541 in {file_path}: {e}")

        return False

    def _parse_flake8_output(self, output: str) -> List[Tuple[str, int, int, str]]:
        """Parse flake8 output into structured violations"""
        violations = []
        for line in output.split('\n'):
            if line.strip() and ':' in line:
                try:
                    # Parse format: ./file.py:line:col: CODE message
                    parts = line.split(':')
                    if len(parts) >= 4:
                        file_path = parts[0]  # Keep original path
                        line_num = int(parts[1])
                        col = int(parts[2])
                        message = ':'.join(parts[3:]).strip()
                        violations.append((file_path, line_num, col, message))
                except (ValueError, IndexError):
                    continue
        return violations

    def run_final_validation(self) -> Dict[str, int]:
        """📊 Execute final validation scan"""
        logger.info("🔍 PHASE 4 FINAL VALIDATION INITIATED...")

        with tqdm(total=100, desc="🔄 Final Validation", unit="%",
                 bar_format="{l_bar}{bar}| {n:.1f}/{total}{unit} [{elapsed}<{remaining}]") as pbar:

            pbar.set_description("🔍 Final flake8 scan")
            try:
                result = subprocess.run(
                    ['python', '-m', 'flake8', '--statistics', '.'],
                    capture_output=True, text=True, encoding='utf-8', cwd=self.workspace_path
                )
                pbar.update(50)

                pbar.set_description("📊 Processing final results")
                final_counts = self._parse_flake8_statistics(result.stdout)
                pbar.update(50)

                # Calculate success metrics
                final_total = sum(final_counts.values())
                total_reduction = self.metrics.total_violations - final_total
                success_rate = (self.metrics.violations_fixed / self.metrics.target_violations * 100) if self.metrics.target_violations > 0 else 0

                logger.info("📊 FINAL VALIDATION COMPLETE")
                logger.info(f"   Total Violations Before: {self.metrics.total_violations:,}")
                logger.info(f"   Total Violations After:  {final_total:,}")
                logger.info(f"   Violations Eliminated:   {total_reduction:,}")
                logger.info(f"   Phase 4 Success Rate:    {success_rate:.1f}%")

            except subprocess.CalledProcessError as e:
                logger.error(f"Final validation failed: {e}")
                final_counts = {}

        return final_counts

    def _parse_flake8_statistics(self, output: str) -> Dict[str, int]:
        """Parse flake8 statistics output"""
        stats = {}
        for line in output.split('\n'):
            if line.strip() and ':' in line:
                try:
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        count = int(parts[0])
                        code = parts[1]
                        stats[code] = count
                except (ValueError, IndexError):
                    continue
        return stats

    def generate_completion_report(self, baseline_counts: Dict[str, int],
                                  final_counts: Dict[str, int],
                                  category_results: Dict[str, Dict[str, Any]]):
        """📋 Generate comprehensive completion report"""
        self.metrics.end_time = datetime.now()
        duration = (self.metrics.end_time - self.metrics.start_time).total_seconds()

        timestamp = self.metrics.end_time.strftime('%Y%m%d_%H%M%S')
        report_file = f"phase4_completion_report_fixed_{timestamp}.txt"

        logger.info("📋 GENERATING COMPLETION REPORT...")

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("PHASE 4 SYSTEMATIC PROCESSING - COMPLETION REPORT (FIXED)\n")
            f.write("="*60 + "\n")
            f.write(f"Generated: {self.metrics.end_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Duration: {duration:.1f} seconds\n")
            f.write(f"Target Violations: {self.metrics.target_violations:,}\n")
            f.write(f"Violations Fixed: {self.metrics.violations_fixed:,}\n")
            f.write(f"Success Rate: {self.metrics.calculate_success_rate():.1f}%\n\n")

            # Category breakdown
            f.write("CATEGORY BREAKDOWN\n")
            f.write("-"*30 + "\n")
            for code, results in category_results.items():
                f.write(f"{code}: {results['fixes_made']:3d} fixes / {results['target_count']:3d} target ({results['success_rate']:.1f}%)\n")

            f.write("\nBASELINE vs FINAL\n")
            f.write("-"*30 + "\n")
            for code in baseline_counts:
                baseline = baseline_counts.get(code, 0)
                final = final_counts.get(code, 0)
                reduction = baseline - final
                f.write(f"{code}: {baseline:3d} -> {final:3d} (reduced: {reduction:3d})\n")

        logger.info(f"📋 Completion report generated: {report_file}")

    def execute_phase4_processing(self):
        """🚀 Execute complete Phase 4 systematic processing"""
        try:
            # Phase 1: Baseline scanning
            logger.info("🔍 PHASE 4 STEP 1: BASELINE SCANNING")
            baseline_counts = self.run_baseline_scan()

            # Phase 2: Category processing
            logger.info("🎯 PHASE 4 STEP 2: CATEGORY PROCESSING")
            category_results = self.process_phase4_categories()

            # Phase 3: Final validation
            logger.info("📊 PHASE 4 STEP 3: FINAL VALIDATION")
            final_counts = self.run_final_validation()

            # Phase 4: Completion reporting
            logger.info("📋 PHASE 4 STEP 4: COMPLETION REPORTING")
            self.generate_completion_report(baseline_counts, final_counts, category_results)

            return True

        except Exception as e:
            logger.error(f"❌ PHASE 4 PROCESSING FAILED: {e}")
            self.metrics.processing_errors.append(f"CRITICAL: {str(e)}")
            return False


def main():
    """🚀 Phase 4 Systematic Processing Entry Point - FIXED VERSION"""
    # MANDATORY: Enterprise startup validation
    print("🚀 PHASE 4 SYSTEMATIC PROCESSOR - FIXED VERSION STARTING...")
    print("🎯 TARGET: 1,159 High-Impact Violations")
    print("🔧 CRITICAL FIX: File path handling corrected")
    print("📊 PROJECTED SUCCESS: 92%+ (1,066+ violations eliminated)")
    print("⏱️  ESTIMATED DURATION: 15-20 minutes")
    print("="*80)

    try:
        processor = Phase4SystematicProcessorFixed()
        success = processor.execute_phase4_processing()

        if success:
            print("="*80)
            print("✅ PHASE 4 SYSTEMATIC PROCESSING COMPLETED SUCCESSFULLY")
            print(f"🎯 Violations Fixed: {processor.metrics.violations_fixed:,}")
            print(f"📊 Success Rate: {processor.metrics.calculate_success_rate():.1f}%")
            print("📋 Check completion report for detailed results")
            print("="*80)
        else:
            print("❌ PHASE 4 PROCESSING FAILED - Check logs for details")

        return success

    except Exception as e:
        print(f"❌ PHASE 4 STARTUP FAILED: {e}")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
