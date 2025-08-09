#!/usr/bin/env python3
"""Safe pytest runner that handles coverage plugin availability."""

import subprocess
import sys
import json
from pathlib import Path
from typing import Dict, Any

def check_pytest_cov_available() -> bool:
    """Check if pytest-cov plugin is available."""
    try:
        import importlib.util
        return importlib.util.find_spec("pytest_cov") is not None
    except ImportError:
        return False

def run_pytest_safe(
    target_path: str = "tests/", 
    output_file: str = "artifacts/test_failures_summary.json"
) -> Dict[str, Any]:
    """Run pytest with coverage if available, otherwise plain pytest."""
    
    # Ensure output directory exists
    json_output = output_file.replace('.json', '.pytest.json')
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    
    # Build command
    if check_pytest_cov_available():
        cmd = ["python", "-m", "pytest", target_path, "-v", "--tb=short", 
               "--cov=.", "--cov-report=term", "--json-report", f"--json-report-file={json_output}"]
        print("✅ pytest-cov available, running with coverage")
    else:
        # Override pytest.ini to avoid cov arguments
        cmd = ["python", "-m", "pytest", target_path, "-v", "--tb=short", 
               "-o", "addopts=", "--json-report", f"--json-report-file={json_output}"]
        print("⚠️ pytest-cov not available, running without coverage")
    
    # Run pytest
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        summary = {
            "command": " ".join(cmd),
            "exit_code": result.returncode,
            "stdout_lines": len(result.stdout.splitlines()),
            "stderr_lines": len(result.stderr.splitlines()),
            "coverage_enabled": check_pytest_cov_available(),
            "success": result.returncode == 0
        }
        
        # Extract test summary from output
        stdout_lower = result.stdout.lower()
        if "failed" in stdout_lower:
            summary["has_failures"] = True
        if "passed" in stdout_lower:
            summary["has_passes"] = True
        if "error" in stdout_lower:
            summary["has_errors"] = True
            
        # Save summary
        with open(output_file, 'w') as f:
            json.dump(summary, f, indent=2)
            
        print(f"📊 Test summary saved to {output_file}")
        print(f"Exit code: {result.returncode}")
        
        if result.stdout:
            print("STDOUT:")
            print(result.stdout[-1000:])  # Last 1000 chars
        if result.stderr:
            print("STDERR:")
            print(result.stderr[-500:])   # Last 500 chars
            
        return summary
        
    except subprocess.TimeoutExpired:
        summary = {
            "command": " ".join(cmd),
            "exit_code": -1,
            "error": "Test execution timed out after 300 seconds",
            "coverage_enabled": check_pytest_cov_available(),
            "success": False
        }
        
        with open(output_file, 'w') as f:
            json.dump(summary, f, indent=2)
            
        return summary

def main():
    """Main entry point for the safe test runner."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Safe pytest runner with coverage handling")
    parser.add_argument("--target", default="tests/", help="Target path for tests")
    parser.add_argument("--output", default="artifacts/test_failures_summary.json", help="Output file for summary")
    
    args = parser.parse_args()
    
    print("🧪 Starting safe pytest execution...")
    summary = run_pytest_safe(args.target, args.output)
    
    if summary["success"]:
        print("✅ All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed or encountered errors")
        sys.exit(1)

if __name__ == "__main__":
    main()
