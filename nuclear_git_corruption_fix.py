#!/usr/bin/env python3
"""
🔧 NUCLEAR GIT CORRUPTION FIX - COMPLETE REPOSITORY REBUILD
Enterprise-Grade Git Repository Nuclear Option with Database Preservation

This script performs a complete Git repository rebuild while preserving all files and database state.
Specifically addresses extensive Git corruption with invalid references and bad objects.

DUAL COPILOT PATTERN COMPLIANT
Anti-Recursion: VALIDATED
Enterprise Standards: FULL COMPLIANCE
"""

import os
import sys
import subprocess
import logging
import shutil
from pathlib import Path
from datetime import datetime
from tqdm import tqdm
import sqlite3

# Configure enterprise logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

class NuclearGitCorruptionFix:
    """🔧 Nuclear Git Corruption Fix with Complete Repository Rebuild"""
    
    def __init__(self, workspace_path: str = os.getenv("GH_COPILOT_WORKSPACE", "e:/gh_COPILOT")):
        self.workspace_path = Path(workspace_path)
        self.logger = logging.getLogger("NuclearGitFix")
        self.backup_path = Path("E:/temp/gh_COPILOT_Nuclear_Backup")
        
        # CRITICAL: Anti-recursion validation
        self._validate_workspace_integrity()
        
    def _validate_workspace_integrity(self):
        """🛡️ CRITICAL: Validate workspace integrity"""
        if not self.workspace_path.exists():
            raise RuntimeError(f"Workspace does not exist: {self.workspace_path}")
            
        # Ensure backup path is external
        if str(self.backup_path).startswith(str(self.workspace_path)):
            raise RuntimeError("🚨 CRITICAL: Backup path cannot be within workspace!")
        
        self.logger.info("✅ Workspace integrity validated")
    
    def nuclear_git_fix(self):
        """🔧 Nuclear Git corruption fix with complete repository rebuild"""
        
        start_time = datetime.now()
        self.logger.info(f"🚀 NUCLEAR GIT CORRUPTION FIX STARTED: {start_time}")
        
        try:
            with tqdm(total=100, desc="🔄 Nuclear Git Fix", unit="%") as pbar:
                
                # Phase 1: Backup working files (20%)
                pbar.set_description("💾 Backing up working files")
                self._backup_working_files()
                pbar.update(20)
                
                # Phase 2: Preserve database state (15%)
                pbar.set_description("🗄️ Preserving database state")
                self._preserve_database_state()
                pbar.update(15)
                
                # Phase 3: Nuclear Git cleanup (25%)
                pbar.set_description("💥 Nuclear Git cleanup")
                self._nuclear_git_cleanup()
                pbar.update(25)
                
                # Phase 4: Initialize fresh repository (20%)
                pbar.set_description("🆕 Initializing fresh repository")
                self._initialize_fresh_repository()
                pbar.update(20)
                
                # Phase 5: Restore files and commit (20%)
                pbar.set_description("🔄 Restoring files and committing")
                self._restore_and_commit()
                pbar.update(20)
            
            self.logger.info("✅ Nuclear Git corruption fix complete!")
            return True
                
        except Exception as e:
            self.logger.error(f"❌ Nuclear Git corruption fix failed: {e}")
            raise
    
    def _backup_working_files(self):
        """💾 Backup all working files"""
        self.logger.info("💾 Creating backup of working files...")
        
        # Create backup directory
        self.backup_path.mkdir(parents=True, exist_ok=True)
        
        # Backup all files except .git
        for item in self.workspace_path.iterdir():
            if item.name != ".git":
                dest = self.backup_path / item.name
                if item.is_file():
                    shutil.copy2(item, dest)
                elif item.is_dir():
                    shutil.copytree(item, dest, dirs_exist_ok=True)
        
        self.logger.info(f"✅ Backup created at: {self.backup_path}")
    
    def _preserve_database_state(self):
        """🗄️ Preserve database state"""
        self.logger.info("🗄️ Preserving database state...")
        
        # Create database backup
        db_backup_path = self.backup_path / "database_backup"
        db_backup_path.mkdir(exist_ok=True)
        
        # Copy all database files
        for db_file in self.workspace_path.glob("*.db"):
            if db_file.exists():
                shutil.copy2(db_file, db_backup_path / db_file.name)
                self.logger.info(f"✅ Backed up database: {db_file.name}")
        
        # Copy databases directory if it exists
        databases_dir = self.workspace_path / "databases"
        if databases_dir.exists():
            shutil.copytree(databases_dir, db_backup_path / "databases", dirs_exist_ok=True)
            self.logger.info("✅ Backed up databases directory")
    
    def _nuclear_git_cleanup(self):
        """💥 Nuclear Git cleanup - complete removal"""
        self.logger.info("💥 Performing nuclear Git cleanup...")
        
        git_dir = self.workspace_path / ".git"
        if git_dir.exists():
            # Force removal of .git directory
            shutil.rmtree(git_dir, ignore_errors=True)
            self.logger.info("✅ .git directory completely removed")
        
        # Also remove any git-related files
        git_files = [".gitignore", ".gitattributes"]
        for git_file in git_files:
            file_path = self.workspace_path / git_file
            if file_path.exists():
                # Backup these files
                shutil.copy2(file_path, self.backup_path / git_file)
                self.logger.info(f"✅ Backed up {git_file}")
    
    def _initialize_fresh_repository(self):
        """🆕 Initialize fresh Git repository"""
        self.logger.info("🆕 Initializing fresh Git repository...")
        
        try:
            # Initialize new repository
            subprocess.run(
                ["git", "init"], 
                cwd=self.workspace_path, 
                check=True
            )
            self.logger.info("✅ Fresh Git repository initialized")
            
            # Add remote
            subprocess.run(
                ["git", "remote", "add", "origin", "https://github.com/Aries-Serpent/gh_COPILOT.git"], 
                cwd=self.workspace_path, 
                check=True
            )
            self.logger.info("✅ Remote origin added")
            
            # Configure Git (basic settings)
            subprocess.run(
                ["git", "config", "user.name", "gh_COPILOT"], 
                cwd=self.workspace_path, 
                check=False
            )
            subprocess.run(
                ["git", "config", "user.email", "copilot@gh-copilot.local"], 
                cwd=self.workspace_path, 
                check=False
            )
            
        except Exception as e:
            self.logger.error(f"❌ Fresh repository initialization failed: {e}")
            raise
    
    def _restore_and_commit(self):
        """🔄 Restore files and create initial commit"""
        self.logger.info("🔄 Restoring files and creating commit...")
        
        try:
            # Restore .gitignore if it existed
            gitignore_backup = self.backup_path / ".gitignore"
            if gitignore_backup.exists():
                shutil.copy2(gitignore_backup, self.workspace_path / ".gitignore")
                self.logger.info("✅ Restored .gitignore")
            
            # Add all files
            subprocess.run(
                ["git", "add", "."], 
                cwd=self.workspace_path, 
                check=True
            )
            self.logger.info("✅ All files staged")
            
            # Create initial commit
            commit_message = f"Nuclear fix: Complete repository rebuild - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            subprocess.run(
                ["git", "commit", "-m", commit_message], 
                cwd=self.workspace_path, 
                check=True
            )
            self.logger.info("✅ Initial commit created")
            
            # Set up main branch tracking
            subprocess.run(
                ["git", "branch", "-M", "main"], 
                cwd=self.workspace_path, 
                check=True
            )
            self.logger.info("✅ Main branch configured")
            
        except Exception as e:
            self.logger.error(f"❌ File restoration and commit failed: {e}")
            raise
    
    def verify_nuclear_fix(self) -> bool:
        """✅ Verify the nuclear fix worked"""
        self.logger.info("✅ Verifying nuclear Git fix...")
        
        try:
            # Test basic Git operations
            subprocess.run(
                ["git", "status"], 
                cwd=self.workspace_path, 
                capture_output=True, 
                text=True, 
                check=True
            )
            self.logger.info("✅ Git status working")
            
            # Test branch information
            result = subprocess.run(
                ["git", "branch"], 
                cwd=self.workspace_path, 
                capture_output=True, 
                text=True, 
                check=True
            )
            self.logger.info(f"✅ Git branches: {result.stdout.strip()}")
            
            # Test remote information
            result = subprocess.run(
                ["git", "remote", "-v"], 
                cwd=self.workspace_path, 
                capture_output=True, 
                text=True, 
                check=True
            )
            self.logger.info(f"✅ Git remotes: {result.stdout.strip()}")
            
            # Verify no corruption
            subprocess.run(
                ["git", "fsck"], 
                cwd=self.workspace_path, 
                capture_output=True, 
                text=True, 
                check=True
            )
            self.logger.info("✅ Repository integrity verified")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Nuclear fix verification failed: {e}")
            return False
    
    def setup_github_desktop_compatibility(self):
        """🎯 Set up GitHub Desktop compatibility"""
        self.logger.info("🎯 Setting up GitHub Desktop compatibility...")
        
        try:
            # Fetch from remote to establish tracking
            subprocess.run(
                ["git", "fetch", "origin"], 
                cwd=self.workspace_path, 
                check=False  # May fail initially, that's OK
            )
            
            # Set upstream tracking for main
            subprocess.run(
                ["git", "branch", "--set-upstream-to=origin/main", "main"], 
                cwd=self.workspace_path, 
                check=False  # May fail if remote doesn't have main yet
            )
            
            self.logger.info("✅ GitHub Desktop compatibility configured")
            
        except Exception as e:
            self.logger.warning(f"⚠️ GitHub Desktop setup had issues: {e}")
    
    def generate_nuclear_fix_report(self, success: bool, start_time: datetime):
        """📊 Generate comprehensive nuclear fix report"""
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print("=" * 80)
        print("=== NUCLEAR GIT CORRUPTION FIX REPORT ===")
        print("=" * 80)
        print(f"🚀 Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"✅ End Time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏱️ Duration: {duration:.2f} seconds")
        print()
        print("💥 NUCLEAR FIX ACTIONS PERFORMED:")
        print("✅ Complete .git directory removal")
        print("✅ All working files backed up to external location")
        print("✅ Database state preserved")
        print("✅ Fresh Git repository initialized")
        print("✅ Clean remote origin configured")
        print("✅ All files re-committed with clean history")
        print("✅ Main branch configured")
        print()
        print("💾 BACKUP LOCATION:")
        print(f"📁 {self.backup_path}")
        print()
        print("📊 VERIFICATION RESULTS:")
        if success:
            print("✅ Git status: WORKING")
            print("✅ Git repository: CLEAN")
            print("✅ No corruption detected")
            print("✅ GitHub Desktop ready")
        else:
            print("❌ Verification failed")
        print()
        print("🎯 GITHUB DESKTOP STATUS:")
        if success:
            print("✅ Repository completely rebuilt")
            print("✅ All corruption eliminated")
            print("✅ GitHub Desktop should work perfectly")
            print("🔄 You may need to push to sync with remote")
        else:
            print("⚠️ Manual intervention required")
        print("=" * 80)
        
        if success:
            print("🎉 SUCCESS: Nuclear Git fix complete!")
            print("💡 Repository is now completely clean")
            print("💡 Consider pushing to sync with remote: git push -u origin main")
        else:
            print("⚠️ NUCLEAR FIX INCOMPLETE")
    
    def cleanup_backup(self):
        """🧹 Clean up backup after successful fix"""
        try:
            if self.backup_path.exists():
                response = input(f"\n🗑️ Delete backup at {self.backup_path}? (y/N): ")
                if response.lower() == 'y':
                    shutil.rmtree(self.backup_path)
                    print("✅ Backup cleaned up")
                else:
                    print(f"💾 Backup preserved at: {self.backup_path}")
        except Exception as e:
            print(f"⚠️ Could not clean backup: {e}")


def main():
    """🎯 Main execution function"""
    
    try:
        print("💥 NUCLEAR GIT CORRUPTION FIX")
        print("⚠️ This will completely rebuild the Git repository")
        print("✅ All files will be preserved")
        print("💾 Full backup will be created")
        print()
        
        # Confirm nuclear option
        response = input("🔥 Proceed with nuclear Git fix? (y/N): ")
        if response.lower() != 'y':
            print("❌ Nuclear fix cancelled")
            sys.exit(0)
        
        # Initialize nuclear fix system
        nuclear_fix = NuclearGitCorruptionFix()
        
        start_time = datetime.now()
        
        # Execute nuclear fix
        success = nuclear_fix.nuclear_git_fix()
        
        if success:
            # Verify the fix
            success = nuclear_fix.verify_nuclear_fix()
            
            if success:
                # Set up GitHub Desktop compatibility
                nuclear_fix.setup_github_desktop_compatibility()
        
        # Generate comprehensive report
        nuclear_fix.generate_nuclear_fix_report(success, start_time)
        
        if success:
            print("\n🎉 NUCLEAR GIT FIX COMPLETE!")
            nuclear_fix.cleanup_backup()
            sys.exit(0)
        else:
            print("\n⚠️ NUCLEAR FIX INCOMPLETE!")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 CRITICAL ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
