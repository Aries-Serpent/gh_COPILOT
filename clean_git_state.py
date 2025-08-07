#!/usr/bin/env python3
"""
🔧 Git State Cleaner and Validator
Ensures git repository is in a completely clean state for VS Code
Generated: 2025-08-06 | Enterprise Standards Compliance
"""

import subprocess
from datetime import datetime
from pathlib import Path

def clean_git_state():
    """Ensure git repository is in completely clean state"""
    
    print("🔧 Git State Cleaner - Ensuring Clean Repository State")
    print("=" * 60)
    
    workspace = Path.cwd()
    git_dir = workspace / ".git"
    
    # Step 1: Reset to clean state
    print("📋 Step 1: Resetting to clean state...")
    try:
        subprocess.run(["git", "reset", "--hard", "HEAD"], check=True, capture_output=True)
        print("✅ Hard reset completed")
    except Exception as e:
        print(f"⚠️ Reset warning: {e}")
    
    # Step 2: Clean untracked files
    print("🧹 Step 2: Cleaning untracked files...")
    try:
        subprocess.run(["git", "clean", "-fd"], check=True, capture_output=True)
        print("✅ Untracked files cleaned")
    except Exception as e:
        print(f"⚠️ Clean warning: {e}")
    
    # Step 3: Remove any merge state files
    print("🗑️ Step 3: Removing merge state files...")
    merge_files = [
        ".git/MERGE_HEAD",
        ".git/MERGE_MSG", 
        ".git/CHERRY_PICK_HEAD",
        ".git/REVERT_HEAD",
        ".git/BISECT_LOG"
    ]
    
    for merge_file in merge_files:
        merge_path = workspace / merge_file
        if merge_path.exists():
            try:
                merge_path.unlink()
                print(f"✅ Removed {merge_file}")
            except Exception as e:
                print(f"⚠️ Could not remove {merge_file}: {e}")
        else:
            print(f"ℹ️ {merge_file} not present")
    
    # Step 4: Verify git status
    print("🔍 Step 4: Verifying git status...")
    try:
        result = subprocess.run(["git", "status", "--porcelain"], 
                              capture_output=True, text=True, check=True)
        if result.stdout.strip():
            print("⚠️ Warning: Working directory not clean:")
            print(result.stdout)
        else:
            print("✅ Working directory is clean")
    except Exception as e:
        print(f"❌ Status check failed: {e}")
    
    # Step 5: Check LFS configuration
    print("🔧 Step 5: Verifying LFS configuration...")
    try:
        result = subprocess.run(["git", "config", "--get", "lfs.skipdownloaderrors"], 
                              capture_output=True, text=True)
        if result.stdout.strip() == "true":
            print("✅ LFS skip configuration is active")
        else:
            print("⚠️ Setting LFS skip configuration...")
            subprocess.run(["git", "config", "lfs.skipdownloaderrors", "true"], check=True)
            print("✅ LFS skip configuration set")
    except Exception as e:
        print(f"⚠️ LFS config warning: {e}")
    
    # Step 6: Test commit capability
    print("🧪 Step 6: Testing commit capability...")
    try:
        # Create a temporary test file
        test_file = workspace / "git_state_test.tmp"
        test_file.write_text(f"Git state test - {datetime.now()}")
        
        # Add and commit
        subprocess.run(["git", "add", "git_state_test.tmp"], check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Git state test commit"], check=True, capture_output=True)
        
        # Remove the test
        subprocess.run(["git", "rm", "git_state_test.tmp"], check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Remove git state test"], check=True, capture_output=True)
        
        print("✅ Git commit capability verified")
        
    except Exception as e:
        print(f"❌ Commit test failed: {e}")
        # Clean up test file if it exists
        test_file = workspace / "git_state_test.tmp"
        if test_file.exists():
            test_file.unlink()
    
    print("=" * 60)
    print("🎉 Git state cleaning completed!")
    print("✅ Repository should now be in a clean state for VS Code")

if __name__ == "__main__":
    clean_git_state()
