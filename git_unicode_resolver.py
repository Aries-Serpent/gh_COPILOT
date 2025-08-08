#!/usr/bin/env python3
"""
🔧 Git Unicode File Resolution Tool
Resolve git conflicts caused by Unicode file paths
"""

import os
import subprocess
import sys
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GitUnicodeResolver:
    """🔧 Resolve git issues caused by Unicode file paths"""
    
    def __init__(self):
        self.workspace = Path.cwd()
        
    def run_git_command(self, command: list, capture_output: bool = True):
        """Execute git command with proper error handling"""
        try:
            if capture_output:
                result = subprocess.run(
                    command,
                    cwd=self.workspace,
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace'
                )
                return result
            else:
                result = subprocess.run(command, cwd=self.workspace, check=True)
                return result
        except subprocess.CalledProcessError as e:
            logger.error(f"Git command failed: {' '.join(command)}")
            logger.error(f"Error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return None
    
    def configure_git_unicode(self):
        """Configure git to handle Unicode properly"""
        logger.info("🔧 Configuring git for Unicode handling...")
        
        configs = [
            ['git', 'config', 'core.quotepath', 'false'],
            ['git', 'config', 'core.precomposeunicode', 'true'],
            ['git', 'config', 'core.autocrlf', 'false']
        ]
        
        for config in configs:
            result = self.run_git_command(config)
            if result and result.returncode == 0:
                logger.info(f"✅ Set: {' '.join(config[2:])}")
            else:
                logger.warning(f"⚠️ Failed to set: {' '.join(config[2:])}")
    
    def attempt_forced_merge(self):
        """Attempt to force merge with Unicode resolution"""
        logger.info("🔄 Attempting forced merge with Unicode resolution...")
        
        # Try merge with strategy
        result = self.run_git_command([
            'git', 'merge', 'origin/gh-codex', 
            '-X', 'theirs', 
            '--allow-unrelated-histories'
        ])
        
        if result and result.returncode == 0:
            logger.info("✅ Forced merge successful")
            return True
        else:
            logger.error("❌ Forced merge failed")
            if result:
                logger.error(f"Error output: {result.stderr}")
            return False
    
    def skip_problematic_file(self):
        """Skip the problematic Unicode file"""
        logger.info("⏭️ Attempting to skip problematic Unicode file...")
        
        # Try to remove problematic file from index
        problematic_patterns = [
            '*White*Paper*Blueprint*2025-08-06*',
            '*White\\342\\200\\221Paper*'
        ]
        
        for pattern in problematic_patterns:
            result = self.run_git_command(['git', 'rm', '--cached', pattern])
            if result and result.returncode == 0:
                logger.info(f"✅ Removed pattern from index: {pattern}")
    
    def reset_and_retry(self):
        """Reset and retry the merge process"""
        logger.info("🔄 Resetting and retrying merge process...")
        
        # Reset to clean state
        result = self.run_git_command(['git', 'reset', '--hard', 'HEAD'])
        if result and result.returncode == 0:
            logger.info("✅ Reset to clean state")
        
        # Try merge again
        return self.attempt_forced_merge()
    
    def checkout_target_branch(self, branch_name: str):
        """Checkout the target branch"""
        logger.info(f"🔄 Checking out branch: {branch_name}")
        
        # First try to checkout existing local branch
        result = self.run_git_command(['git', 'checkout', branch_name])
        if result and result.returncode == 0:
            logger.info(f"✅ Checked out existing branch: {branch_name}")
            return True
        
        # Try to create and checkout from remote
        result = self.run_git_command([
            'git', 'checkout', '-b', branch_name, f'origin/{branch_name}'
        ])
        if result and result.returncode == 0:
            logger.info(f"✅ Created and checked out branch: {branch_name}")
            return True
        
        logger.error(f"❌ Failed to checkout branch: {branch_name}")
        return False
    
    def resolve_conflicts(self):
        """Main resolution workflow"""
        logger.info("="*60)
        logger.info("🚀 STARTING GIT UNICODE CONFLICT RESOLUTION")
        logger.info("="*60)
        
        # Step 1: Configure git for Unicode
        self.configure_git_unicode()
        
        # Step 2: Skip problematic file
        self.skip_problematic_file()
        
        # Step 3: Try forced merge
        if self.attempt_forced_merge():
            logger.info("✅ Merge successful after Unicode configuration")
            return True
        
        # Step 4: Reset and retry
        if self.reset_and_retry():
            logger.info("✅ Merge successful after reset")
            return True
        
        # Step 5: Try checkout target branch directly
        target_branch = "codex/create-session-protection-workflow-and-alias"
        if self.checkout_target_branch(target_branch):
            logger.info("✅ Successfully checked out target branch")
            
            # Try merge from gh-codex
            result = self.run_git_command(['git', 'merge', 'gh-codex'])
            if result and result.returncode == 0:
                logger.info("✅ Merge successful from target branch")
                return True
        
        logger.error("❌ All resolution attempts failed")
        return False

def main():
    """Main execution"""
    resolver = GitUnicodeResolver()
    
    try:
        success = resolver.resolve_conflicts()
        if success:
            print("🎯 Git Unicode conflict resolution: SUCCESS")
            return 0
        else:
            print("❌ Git Unicode conflict resolution: FAILED")
            return 1
    except Exception as e:
        logger.error(f"💥 Critical error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
