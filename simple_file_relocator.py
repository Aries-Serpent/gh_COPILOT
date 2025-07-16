#!/usr/bin/env python3
"""
Simple File Relocator for Enterprise File Organization
Database-Driven File Management with Visual Processing
"""

import os
import shutil
import json
from pathlib import Path
from datetime import datetime

# Configuration
WORKSPACE_ROOT = Path(os.getenv("GH_COPILOT_WORKSPACE", "e:/gh_COPILOT"))

def ensure_directories():
    """Ensure target directories exist"""
    dirs = ["logs", "documentation", "reports", "results"]
    for dir_name in dirs:
        (WORKSPACE_ROOT / dir_name).mkdir(exist_ok=True)
        print(f"Directory ensured: {dir_name}/")

def get_files_to_move():
    """Get files that need to be moved"""
    
    # Log files to move to logs/
    log_files = [
        "autonomous_cli.log", "autonomous_monitoring.log", "autonomous_optimization.log",
        "compliance_scan_20250710_173622.log", "compliance_scan_20250710_173707.log",
        "database_cleanup.log", "emergency_cleanup.log", "enterprise_audit.log",
        "flake8_compliance.log", "syntax_fixer.log", "validation_output.log"
    ]
    
    # Documentation files to move to documentation/ (excluding README.md)
    doc_files = [
        "AGENTS.md", "CHANGELOG.md", "AUTONOMOUS_CLI_DEPLOYMENT_COMPLETE.md",
        "COMPLETE_TECHNICAL_SPECIFICATIONS_WHITEPAPER.md", "FAREWELL_MESSAGE.md"
    ]
    
    # Report files to move to reports/
    report_files = [
        "compliance_report.json", "aggressive_compression_report_20250710_164134.json",
        "comprehensive_campaign_final_report_20250713_111239.json"
    ]
    
    # Result files to move to results/
    result_files = [
        "quick_database_validation_results.json", "database_validation_results.json"
    ]
    
    files_to_move = {}
    
    # Build move map
    for file in log_files:
        src = WORKSPACE_ROOT / file
        dest = WORKSPACE_ROOT / "logs" / file
        if src.exists():
            files_to_move[str(src)] = str(dest)
    
    for file in doc_files:
        src = WORKSPACE_ROOT / file
        dest = WORKSPACE_ROOT / "documentation" / file
        if src.exists():
            files_to_move[str(src)] = str(dest)
    
    for file in report_files:
        src = WORKSPACE_ROOT / file
        dest = WORKSPACE_ROOT / "reports" / file
        if src.exists():
            files_to_move[str(src)] = str(dest)
    
    for file in result_files:
        src = WORKSPACE_ROOT / file
        dest = WORKSPACE_ROOT / "results" / file
        if src.exists():
            files_to_move[str(src)] = str(dest)
    
    return files_to_move

def move_files(files_to_move):
    """Move files with progress tracking"""
    results = {
        "total_files": len(files_to_move),
        "successful_moves": 0,
        "failed_moves": 0,
        "moved_files": [],
        "failed_files": []
    }
    
    print(f"Starting relocation of {len(files_to_move)} files...")
    
    for i, (src, dest) in enumerate(files_to_move.items(), 1):
        try:
            shutil.move(src, dest)
            results["successful_moves"] += 1
            results["moved_files"].append({"src": src, "dest": dest})
            print(f"[{i}/{len(files_to_move)}] MOVED: {Path(src).name} -> {Path(dest).parent.name}/")
        except Exception as e:
            results["failed_moves"] += 1
            results["failed_files"].append({"src": src, "error": str(e)})
            print(f"[{i}/{len(files_to_move)}] FAILED: {Path(src).name} - {e}")
    
    return results

def save_report(results):
    """Save relocation report"""
    report_data = {
        "session_id": f"SIMPLE_RELOCATION_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "timestamp": datetime.now().isoformat(),
        "workspace_root": str(WORKSPACE_ROOT),
        "results": results
    }
    
    report_path = WORKSPACE_ROOT / "reports" / f"simple_relocation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(report_path, 'w') as f:
        json.dump(report_data, f, indent=2)
    
    print(f"Report saved: {report_path}")
    return report_path

def main():
    """Main execution"""
    print("=" * 60)
    print("ENTERPRISE FILE RELOCATION - SIMPLE MODE")
    print("=" * 60)
    
    # Ensure directories
    ensure_directories()
    
    # Get files to move
    files_to_move = get_files_to_move()
    
    if not files_to_move:
        print("No files to relocate.")
        return
    
    # Move files
    results = move_files(files_to_move)
    
    # Save report
    report_path = save_report(results)
    
    # Summary
    print("=" * 60)
    print("RELOCATION SUMMARY")
    print("=" * 60)
    print(f"Total Files: {results['total_files']}")
    print(f"Successful: {results['successful_moves']}")
    print(f"Failed: {results['failed_moves']}")
    print(f"Success Rate: {(results['successful_moves']/results['total_files']*100):.1f}%")
    print("=" * 60)

if __name__ == "__main__":
    main()
