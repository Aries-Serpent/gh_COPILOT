#!/usr/bin/env python3
"""Enhanced Base64 Image Transformer - Launcher"""
import sys
import subprocess
import os

def main():
    print("🚀 Enhanced Base64 Image Transformer")
    print("=" * 40)
    
    # Check if main.py exists
    if not os.path.exists("main.py"):
        print("❌ main.py not found!")
        return 1
    
    try:
        # Run the main application
        print("Starting application...")
        result = subprocess.run([sys.executable, "main.py"])
        return result.returncode
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure PyQt6 is installed:")
        print("   pip install PyQt6")
        return 1

if __name__ == "__main__":
    sys.exit(main())
