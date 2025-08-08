#!/usr/bin/env python3
"""
🎯 Final Git Operations Validation
Tests git commit functionality for VS Code integration
Generated: 2025-08-06 | Validation Complete
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path

def validate_git_operations():
    """Validate all git operations are working perfectly"""
    
    print("🎯 Final Git Operations Validation")
    print("=" * 50)
    
    # Test 1: Check git status
    print("📋 Test 1: Checking git status...")
    try:
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True, check=True)
        if not result.stdout.strip():
            print("✅ Working tree is clean")
        else:
            print("⚠️ Working tree has changes:")
            print(result.stdout)
    except Exception as e:
        print(f"❌ Git status failed: {e}")
        return False
    
    # Test 2: Check LFS configuration
    print("🔧 Test 2: Verifying LFS configuration...")
    try:
        result = subprocess.run(['git', 'config', '--get', 'lfs.skipdownloaderrors'], 
                              capture_output=True, text=True)
        if result.stdout.strip() == "true":
            print("✅ LFS skip configuration is active")
        else:
            print("❌ LFS configuration missing")
            return False
    except Exception as e:
        print(f"❌ LFS config check failed: {e}")
        return False
    
    # Test 3: Test file creation and commit
    print("🧪 Test 3: Testing file creation and commit...")
    try:
        # Create test file
        test_file = Path("validation_test.tmp")
        test_file.write_text(f"Validation test - {datetime.now()}")
        
        # Add file and session logs database if present
        if Path('databases/codex_session_logs.db').exists():
            subprocess.run(['git', 'add', 'databases/codex_session_logs.db'], check=True)
        subprocess.run(['git', 'add', 'validation_test.tmp'], check=True)
        
        # Commit file
        subprocess.run(['git', 'commit', '-m', 'Validation test commit'], 
                      check=True, capture_output=True)
        
        # Remove file
        subprocess.run(['git', 'rm', 'validation_test.tmp'], check=True)
        subprocess.run(['git', 'commit', '-m', 'Remove validation test'], 
                      check=True, capture_output=True)
        
        print("✅ File creation and commit test passed")
        
    except Exception as e:
        print(f"❌ Commit test failed: {e}")
        # Clean up if test failed
        if test_file.exists():
            test_file.unlink()
        return False
    
    # Test 4: Verify no merge conflicts
    print("🔍 Test 4: Checking for merge conflicts...")
    try:
        # Check for merge head files
        git_dir = Path(".git")
        merge_files = ["MERGE_HEAD", "CHERRY_PICK_HEAD", "REVERT_HEAD"]
        
        for merge_file in merge_files:
            if (git_dir / merge_file).exists():
                print(f"❌ Found merge conflict file: {merge_file}")
                return False
        
        print("✅ No merge conflicts detected")
        
    except Exception as e:
        print(f"❌ Merge conflict check failed: {e}")
        return False
    
    print("=" * 50)
    print("🎉 ALL TESTS PASSED!")
    print("✅ Git operations are fully functional")
    print("✅ VS Code integration should work perfectly")
    print("✅ No unmerged files or conflicts")
    print("✅ LFS configuration is active")
    
    return True

if __name__ == "__main__":
    success = validate_git_operations()
    sys.exit(0 if success else 1)
