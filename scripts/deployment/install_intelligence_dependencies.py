#!/usr/bin/env python3
"""
[PACKAGE] INTELLIGENCE PLATFORM DEPENDENCY INSTALLER
==============================================

Installs required packages for Enhanced Analytics Intelligence Platform
"""

import subprocess
import sys
from datetime import datetime

def install_dependencies():
    """Install required dependencies for intelligence platform"""
    start_time = datetime.now()
    print("[LAUNCH] INSTALLING INTELLIGENCE PLATFORM DEPENDENCIES")
    print(f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    dependencies = [
        'scikit-learn',  # For ML algorithms
        'pandas',        # For data analysis
        'numpy',         # For numerical computing
        'flask',         # For web API
        'flask-socketio', # For real-time updates
        'plotly',        # For visualization
        'psutil'         # For system monitoring
    ]
    
    print(f"[PACKAGE] Installing {len(dependencies)} packages...")
    
    for i, package in enumerate(dependencies, 1):
        try:
            print(f"[?] ({i}/{len(dependencies)}) Installing {package}...")
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'install', package
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print(f"[SUCCESS] {package} installed successfully")
            else:
                print(f"[WARNING] {package} installation warning: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print(f"[TIME] {package} installation timeout - continuing...")
        except Exception as e:
            print(f"[ERROR] {package} installation error: {e}")
    
    end_time = datetime.now()
    duration = end_time - start_time
    print(f"\n[BAR_CHART] DEPENDENCY INSTALLATION COMPLETE")
    print(f"Duration: {duration}")
    print(f"[SUCCESS] Intelligence Platform Ready for Execution")

if __name__ == "__main__":
    install_dependencies()
