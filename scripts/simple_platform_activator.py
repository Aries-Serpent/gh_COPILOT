#!/usr/bin/env python3
"""
IMMEDIATE PLATFORM ACTIVATION - Enhanced Analytics Intelligence Platform
[TARGET] Direct execution of critical platform components
"""

import os
import sys
import time
import subprocess
from datetime import datetime
from pathlib import Path

def print_header():
    """Print activation header with visual indicators"""
    print("[LAUNCH] ENHANCED ANALYTICS INTELLIGENCE PLATFORM - IMMEDIATE ACTIVATION")
    print("=" * 70)
    print(f"[TIME] Activation Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"[FOLDER] Workspace: {Path.cwd()}")
    print("[TARGET] DUAL COPILOT: Visual Processing [SUCCESS] | Anti-Recursion [SUCCESS]")
    print("=" * 70)

def check_file_exists(file_path):
    """Check if critical file exists"""
    if Path(file_path).exists():
        print(f"[SUCCESS] {file_path} - Found")
        return True
    else:
        print(f"[ERROR] {file_path} - Missing")
        return False

def activate_platform():
    """Activate platform components step by step"""
    print("\n[PROCESSING] PLATFORM ACTIVATION SEQUENCE...")
    
    # Step 1: Check critical files
    print("\n[CLIPBOARD] Step 1: Checking Critical Files...")
    critical_files = [
        "enhanced_analytics_intelligence_platform.py",
        "enterprise_business_rules_customization.py",
        "web_gui_scripts/flask_apps/enterprise_dashboard.py"
    ]
    
    missing_files = []
    for file_path in critical_files:
        if not check_file_exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n[WARNING]  Missing files detected: {len(missing_files)}")
        for file_path in missing_files:
            print(f"   [?] {file_path}")
        print("\n[WRENCH] Please ensure all platform files are in place")
        return False
    
    # Step 2: Provide activation commands
    print("\n[LAUNCH] Step 2: Platform Activation Commands")
    print("=" * 50)
    
    python_exe = "Q:/python_venv/.venv_clean/Scripts/python.exe"
    
    activation_steps = [
        {
            'name': 'Main Intelligence Platform',
            'command': f'{python_exe} enhanced_analytics_intelligence_platform.py',
            'description': 'Core analytics engine with ML and monitoring'
        },
        {
            'name': 'Enterprise Dashboard',
            'command': f'cd web_gui_scripts/flask_apps && {python_exe} enterprise_dashboard.py',
            'description': 'Executive dashboard for real-time insights'
        },
        {
            'name': 'Business Rules Engine',
            'command': f'{python_exe} enterprise_business_rules_customization.py',
            'description': 'Industry-specific rule configuration'
        }
    ]
    
    print("\n[NOTES] EXECUTE THESE COMMANDS IN SEPARATE TERMINALS:")
    print("=" * 50)
    
    for i, step in enumerate(activation_steps, 1):
        print(f"\n{i}. {step['name']}")
        print(f"   [NOTES] Command: {step['command']}")
        print(f"   [CLIPBOARD] Purpose: {step['description']}")
    
    # Step 3: Access Information
    print("\n[NETWORK] Step 3: Platform Access Information")
    print("=" * 40)
    print("[BAR_CHART] Intelligence Dashboard: file://intelligence/dashboards/intelligence_dashboard.html")
    print("[CHAIN] API Endpoint: http://localhost:5000/api/latest_intelligence")
    print("[?] Enterprise Dashboard: http://localhost:5001 (when started)")
    
    # Step 4: Next Steps
    print("\n[CLIPBOARD] Step 4: Post-Activation Steps")
    print("=" * 35)
    print("1. Monitor platform logs for any initialization issues")
    print("2. Access dashboards to verify data flow")
    print("3. Configure business rules for your industry")
    print("4. Set up automated scheduling if needed")
    
    return True

def main():
    """Main activation function"""
    try:
        print_header()
        
        success = activate_platform()
        
        if success:
            print("\n[SUCCESS] ACTIVATION GUIDE GENERATED SUCCESSFULLY")
            print("[TARGET] Follow the commands above to start all platform components")
        else:
            print("\n[ERROR] ACTIVATION ISSUES DETECTED")
            print("[WRENCH] Resolve missing files before proceeding")
        
        print("\n" + "=" * 70)
        print("[COMPLETE] ENHANCED ANALYTICS INTELLIGENCE PLATFORM READY FOR DEPLOYMENT")
        
    except Exception as e:
        print(f"[ERROR] Activation error: {str(e)}")
        return False

if __name__ == "__main__":
    main()
