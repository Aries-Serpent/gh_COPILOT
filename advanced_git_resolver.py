#!/usr/bin/env python3
"""
🔧 Advanced Git Conflict Resolution
Handle the Unicode file issue by creating a custom merge strategy
"""

import subprocess
import tempfile
import os
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AdvancedGitResolver:
    """Advanced Git conflict resolution with file exclusion"""
    
    def __init__(self):
        self.workspace = Path.cwd()
    
    def run_command(self, cmd, capture_output=True):
        """Run command with error handling"""
        try:
            if capture_output:
                result = subprocess.run(
                    cmd, shell=True, cwd=self.workspace,
                    capture_output=True, text=True, encoding='utf-8', errors='replace'
                )
            else:
                result = subprocess.run(cmd, shell=True, cwd=self.workspace, check=True)
            return result
        except Exception as e:
            logger.error(f"Command failed: {cmd}")
            logger.error(f"Error: {e}")
            return None
    
    def create_merge_without_problematic_file(self):
        """Create a merge that excludes the problematic Unicode file"""
        logger.info("🔄 Creating merge without problematic Unicode file...")
        
        # Step 1: Create a temporary branch to work with
        temp_branch = "temp-unicode-fix"
        
        # Checkout a new temporary branch based on current HEAD
        result = self.run_command(f"git checkout -b {temp_branch}")
        if not result or result.returncode != 0:
            logger.error("Failed to create temporary branch")
            return False
        
        logger.info(f"✅ Created temporary branch: {temp_branch}")
        
        # Step 2: Fetch the latest remote changes
        result = self.run_command("git fetch origin gh-codex")
        if not result or result.returncode != 0:
            logger.error("Failed to fetch remote changes")
            return False
        
        # Step 3: Try to merge specific commits, skipping the problematic one
        # First, let's try to identify which commits we can safely merge
        result = self.run_command("git log --oneline origin/gh-codex ^HEAD")
        if result and result.returncode == 0:
            commits = result.stdout.strip().split('\n')
            logger.info(f"Found {len(commits)} commits to potentially merge")
            
            # Try to cherry-pick commits one by one, skipping problematic ones
            for commit_line in reversed(commits):  # Start from oldest
                if commit_line.strip():
                    commit_hash = commit_line.split()[0]
                    logger.info(f"Attempting to cherry-pick: {commit_hash}")
                    
                    result = self.run_command(f"git cherry-pick {commit_hash}")
                    if result and result.returncode == 0:
                        logger.info(f"✅ Successfully cherry-picked: {commit_hash}")
                    else:
                        logger.warning(f"⚠️ Skipped problematic commit: {commit_hash}")
                        # Reset any partial cherry-pick
                        self.run_command("git cherry-pick --abort")
                        continue
        
        # Step 4: Switch back to gh-codex and merge our temp branch
        result = self.run_command("git checkout gh-codex")
        if not result or result.returncode == 0:
            result = self.run_command(f"git merge {temp_branch}")
            if result and result.returncode == 0:
                logger.info("✅ Successfully merged without problematic file")
                # Clean up temp branch
                self.run_command(f"git branch -d {temp_branch}")
                return True
        
        return False
    
    def alternative_merge_strategy(self):
        """Alternative approach using rebase"""
        logger.info("🔄 Trying alternative merge strategy...")
        
        # Step 1: Create sparse checkout to exclude problematic file
        result = self.run_command("git config core.sparseCheckout true")
        if result and result.returncode == 0:
            logger.info("✅ Enabled sparse checkout")
            
            # Create sparse-checkout file
            sparse_checkout_path = self.workspace / ".git" / "info" / "sparse-checkout"
            try:
                with open(sparse_checkout_path, 'w') as f:
                    f.write("/*\n")
                    f.write("!documentation/generated/daily_state_update/*White*Paper*Blueprint*2025-08-06*\n")
                logger.info("✅ Created sparse-checkout exclusion")
                
                # Apply sparse checkout
                result = self.run_command("git read-tree -m -u HEAD")
                if result and result.returncode == 0:
                    logger.info("✅ Applied sparse checkout")
                
                # Now try merge again
                result = self.run_command("git merge origin/gh-codex")
                if result and result.returncode == 0:
                    logger.info("✅ Merge successful with sparse checkout")
                    return True
                    
            except Exception as e:
                logger.error(f"Failed to create sparse-checkout: {e}")
        
        return False
    
    def manual_checkout_target_branch(self):
        """Manually create the target branch from remote"""
        logger.info("🔄 Manually creating target branch...")
        
        target_branch = "codex/create-session-protection-workflow-and-alias"
        
        # Step 1: Fetch the remote branch
        result = self.run_command(f"git fetch origin {target_branch}")
        if not result or result.returncode != 0:
            logger.error(f"Failed to fetch remote branch: {target_branch}")
            return False
        
        # Step 2: Try to create local branch from specific commit
        # Let's find a safe commit to start from
        result = self.run_command(f"git log --oneline origin/{target_branch} | head -1")
        if result and result.returncode == 0:
            latest_commit = result.stdout.strip().split()[0]
            logger.info(f"Latest commit on target branch: {latest_commit}")
            
            # Create branch from this commit
            result = self.run_command(f"git checkout -b {target_branch} {latest_commit}")
            if result and result.returncode == 0:
                logger.info(f"✅ Successfully created branch: {target_branch}")
                return True
        
        return False
    
    def resolve_git_conflicts(self):
        """Main resolution workflow"""
        logger.info("="*60)
        logger.info("🚀 ADVANCED GIT CONFLICT RESOLUTION")
        logger.info("="*60)
        
        # Strategy 1: Try merge without problematic file
        if self.create_merge_without_problematic_file():
            logger.info("✅ Resolution successful via cherry-pick strategy")
            return True
        
        # Strategy 2: Try sparse checkout approach  
        if self.alternative_merge_strategy():
            logger.info("✅ Resolution successful via sparse checkout")
            return True
        
        # Strategy 3: Manual target branch creation
        if self.manual_checkout_target_branch():
            logger.info("✅ Successfully created target branch manually")
            return True
        
        logger.error("❌ All resolution strategies failed")
        return False

def main():
    resolver = AdvancedGitResolver()
    
    try:
        if resolver.resolve_git_conflicts():
            print("🎯 Advanced Git conflict resolution: SUCCESS")
            return 0
        else:
            print("❌ Advanced Git conflict resolution: FAILED")
            return 1
    except Exception as e:
        logger.error(f"💥 Critical error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
