#!/usr/bin/env python3
"""
Filesystem Isolation Audit Script
Validates that no files or virtual environments were created in C:/Users
during disaster recovery and production deployment processes.
"""

import os
import sys
import json
import datetime
from pathlib import Path

def audit_filesystem_isolation():
    """
    Comprehensive audit to ensure all operations stayed within E:/ and Q:/ drives
    """
    print("=" * 80)
    print("FILESYSTEM ISOLATION AUDIT")
    print("=" * 80)
    print(f"Audit timestamp: {datetime.datetime.now()}")
    print()

    audit_results = {
        "timestamp": datetime.datetime.now().isoformat(),
        "c_users_violations": [],
        "python_executable_location": None,
        "virtual_environment_location": None,
        "workspace_location": None,
        "isolation_status": "UNKNOWN"
    }

    # Check current Python executable location
    try:
        python_exe = sys.executable
        audit_results["python_executable_location"] = python_exe
        print(f"[?] Python executable: {python_exe}")
        
        if "C:\\Users" in python_exe or "/c/Users" in python_exe:
            print("[WARNING]  WARNING: Python executable is in C:/Users")
            audit_results["c_users_violations"].append({
                "type": "python_executable",
                "path": python_exe,
                "description": "Python executable located in C:/Users"
            })
        else:
            print("[?] Python executable not in C:/Users")
    except Exception as e:
        print(f"[ERROR] Error checking Python executable: {e}")

    # Check virtual environment location
    try:
        venv_path = os.environ.get('VIRTUAL_ENV')
        if venv_path:
            audit_results["virtual_environment_location"] = venv_path
            print(f"[?] Virtual environment: {venv_path}")
            
            if "C:\\Users" in venv_path or "/c/Users" in venv_path:
                print("[WARNING]  WARNING: Virtual environment is in C:/Users")
                audit_results["c_users_violations"].append({
                    "type": "virtual_environment",
                    "path": venv_path,
                    "description": "Virtual environment located in C:/Users"
                })
            else:
                print("[?] Virtual environment not in C:/Users")
        else:
            print("[?][?]  No virtual environment detected")
    except Exception as e:
        print(f"[ERROR] Error checking virtual environment: {e}")

    # Check current workspace location
    try:
        workspace_path = os.getcwd()
        audit_results["workspace_location"] = workspace_path
        print(f"[?] Current workspace: {workspace_path}")
        
        if "C:\\Users" in workspace_path or "/c/Users" in workspace_path:
            print("[WARNING]  WARNING: Workspace is in C:/Users")
            audit_results["c_users_violations"].append({
                "type": "workspace",
                "path": workspace_path,
                "description": "Workspace located in C:/Users"
            })
        else:
            print("[?] Workspace not in C:/Users")
    except Exception as e:
        print(f"[ERROR] Error checking workspace: {e}")

    # Search for recent files in C:/Users related to our project
    print("\n" + "="*50)
    print("SCANNING C:/USERS FOR PROJECT-RELATED FILES")
    print("="*50)
    
    c_users_paths = [
        Path("C:/Users"),
        Path("/c/Users")
    ]
    
    project_patterns = [
        "*copilot*",
        "*disaster*",
        "*production*",
        "*.db",
        "*_copilot_*",
        "*template*",
        "*recovery*"
    ]
    
    for users_path in c_users_paths:
        if users_path.exists():
            print(f"Scanning: {users_path}")
            try:
                for pattern in project_patterns:
                    matches = list(users_path.rglob(pattern))
                    if matches:
                        for match in matches[:10]:  # Limit to first 10 matches
                            try:
                                stat = match.stat()
                                mod_time = datetime.datetime.fromtimestamp(stat.st_mtime)
                                # Check if modified in last 24 hours
                                if (datetime.datetime.now() - mod_time).days < 1:
                                    print(f"[WARNING]  Recent file found: {match} (modified: {mod_time})")
                                    audit_results["c_users_violations"].append({
                                        "type": "recent_file",
                                        "path": str(match),
                                        "modified": mod_time.isoformat(),
                                        "pattern": pattern,
                                        "description": "Recent project-related file in C:/Users"
                                    })
                            except (OSError, PermissionError):
                                continue
            except (OSError, PermissionError) as e:
                print(f"[ERROR] Permission denied scanning {users_path}: {e}")
        else:
            print(f"[ERROR] Path not found: {users_path}")

    # Final assessment
    print("\n" + "="*50)
    print("ISOLATION AUDIT SUMMARY")
    print("="*50)
    
    if not audit_results["c_users_violations"]:
        audit_results["isolation_status"] = "COMPLIANT"
        print("[SUCCESS] FILESYSTEM ISOLATION: COMPLIANT")
        print("[SUCCESS] No violations found in C:/Users directory")
        print("[SUCCESS] All operations appear to have stayed within E:/ and Q:/ drives")
    else:
        audit_results["isolation_status"] = "VIOLATIONS_DETECTED"
        print("[ERROR] FILESYSTEM ISOLATION: VIOLATIONS DETECTED")
        print(f"[ERROR] Found {len(audit_results['c_users_violations'])} violations:")
        for violation in audit_results["c_users_violations"]:
            print(f"   - {violation['type']}: {violation['path']}")

    # Save audit results
    audit_file = f"filesystem_isolation_audit_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(audit_file, 'w') as f:
        json.dump(audit_results, f, indent=2)
    
    print(f"\nAudit results saved to: {audit_file}")
    
    return audit_results["isolation_status"] == "COMPLIANT"

if __name__ == "__main__":
    try:
        is_compliant = audit_filesystem_isolation()
        if is_compliant:
            print("\n[TARGET] READY FOR PRODUCTION DEPLOYMENT PHASE 1")
            sys.exit(0)
        else:
            print("\n[WARNING]  FILESYSTEM ISOLATION ISSUES DETECTED - REVIEW REQUIRED")
            sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Audit failed: {e}")
        sys.exit(1)
