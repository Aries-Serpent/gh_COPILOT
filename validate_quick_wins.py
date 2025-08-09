#!/usr/bin/env python3
"""Validation script for the three quick-win targets implemented."""

import sys
import subprocess
from pathlib import Path
import json


def main():
    """Validate the three implemented targets."""
    print("🎯 Quick Wins Validation (Targets 5, 6, 7)\n")
    
    success_count = 0
    total_tests = 3
    
    # Target 5: Composite bounds test
    print("🧮 Target 5: Composite bounds test")
    try:
        result = subprocess.run([
            sys.executable, "scripts/run_tests_safe.py", 
            "--target", "tests/compliance/test_composite_bounds.py"
        ], capture_output=True, text=True, cwd=Path.cwd())
        
        if result.returncode == 0:
            print("   ✅ Composite bounds test: PASSED")
            success_count += 1
        else:
            print("   ❌ Composite bounds test: FAILED")
            print(f"      Error: {result.stderr[:200]}")
    except Exception as e:
        print(f"   ❌ Composite bounds test: ERROR - {e}")
    
    # Target 6: Edge-case ingestion test  
    print("\n📥 Target 6: Edge-case ingestion test")
    try:
        result = subprocess.run([
            sys.executable, "scripts/run_tests_safe.py",
            "--target", "tests/compliance/test_ingestion_edge_cases.py"
        ], capture_output=True, text=True, cwd=Path.cwd())
        
        if result.returncode == 0:
            print("   ✅ Ingestion edge cases test: PASSED")
            success_count += 1
        else:
            print("   ❌ Ingestion edge cases test: FAILED")
            print(f"      Error: {result.stderr[:200]}")
    except Exception as e:
        print(f"   ❌ Ingestion edge cases test: ERROR - {e}")
    
    # Target 7: Coverage absence logging
    print("\n📊 Target 7: Coverage absence logging")
    try:
        # Check artifacts created by safe test runner
        coverage_log = Path("artifacts/coverage_disabled.log")
        test_summary = Path("artifacts/test_failures_summary.json")
        
        if coverage_log.exists() and test_summary.exists():
            # Check log content
            log_content = coverage_log.read_text()
            if "pytest-cov plugin not available" in log_content:
                print("   ✅ Coverage absence log: CREATED & VALID")
                
                # Check test summary JSON
                summary_data = json.loads(test_summary.read_text())
                if "coverage_enabled" in summary_data and not summary_data["coverage_enabled"]:
                    print("   ✅ Test summary JSON: VALID")
                    success_count += 1
                else:
                    print("   ❌ Test summary JSON: Invalid coverage_enabled field")
            else:
                print("   ❌ Coverage absence log: Invalid content")
        else:
            print("   ❌ Coverage absence artifacts: Missing files")
            print(f"      coverage_log exists: {coverage_log.exists()}")
            print(f"      test_summary exists: {test_summary.exists()}")
    except Exception as e:
        print(f"   ❌ Coverage absence logging: ERROR - {e}")
    
    # Final summary
    print(f"\n🎯 SUMMARY: {success_count}/{total_tests} targets completed successfully")
    
    if success_count == total_tests:
        print("🎉 All quick wins implemented and validated!")
        return True
    else:
        print("⚠️  Some targets need attention")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
