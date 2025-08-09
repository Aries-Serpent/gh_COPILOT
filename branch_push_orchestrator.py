#!/usr/bin/env python3
"""
🚀 BRANCH PUSH ORCHESTRATOR
Enterprise Branch Push with Visual Monitoring
Pushes the reset main branch (now matching initial) to remote
"""

import os
import subprocess
import logging
from datetime import datetime
from pathlib import Path
from tqdm import tqdm
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('branch_push.log')
    ]
)
logger = logging.getLogger(__name__)

class BranchPushOrchestrator:
    """🚀 Enterprise Branch Push with Visual Monitoring"""
    
    def __init__(self, workspace_path=None):
        self.workspace_path = Path(workspace_path or os.getcwd())
        self.start_time = datetime.now()
        self.process_id = os.getpid()
        
        # MANDATORY: Initialize visual monitoring
        self.setup_visual_monitoring()
        
        # CRITICAL: Environment validation
        self.validate_environment_compliance()
    
    def setup_visual_monitoring(self):
        """MANDATORY: Setup comprehensive visual indicators"""
        logger.info("="*60)
        logger.info("BRANCH PUSH ORCHESTRATOR INITIALIZED")
        logger.info(f"Task: Push main branch (reset to initial) to remote")
        logger.info(f"Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Process ID: {self.process_id}")
        logger.info(f"Workspace: {self.workspace_path}")
        logger.info("="*60)
    
    def validate_environment_compliance(self):
        """CRITICAL: Validate proper environment setup"""
        logger.info("Validating environment compliance...")
        
        # Validate we're in a git repository
        if not (self.workspace_path / '.git').exists():
            raise RuntimeError("CRITICAL: Not in a git repository")
        
        # Change to workspace directory
        os.chdir(self.workspace_path)
        logger.info("ENVIRONMENT COMPLIANCE VALIDATED")
    
    def run_git_command(self, command: list, description: str = "", check_output: bool = True):
        """Execute git command with error handling"""
        logger.info(f"Executing: {' '.join(command)}")
        if description:
            logger.info(f"   Purpose: {description}")
        
        try:
            if check_output:
                result = subprocess.run(command, capture_output=True, text=True, check=True)
                return result.stdout.strip()
            else:
                subprocess.run(command, check=True)
                return None
        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed: {' '.join(command)}")
            logger.error(f"   Error: {e.stderr}")
            raise
    
    def verify_current_state(self):
        """Verify current branch state before pushing"""
        logger.info("Verifying current branch state...")
        
        # Check current branch
        current_branch = self.run_git_command(['git', 'branch', '--show-current'], 
                                            "Get current branch name")
        if current_branch != 'main':
            raise ValueError(f"CRITICAL: Not on main branch (currently on: {current_branch})")
        
        # Check that main matches initial
        diff_result = self.run_git_command(['git', 'diff', 'main', 'initial'],
                                         "Verify main matches initial")
        if diff_result.strip():
            raise ValueError("CRITICAL: main and initial branches are not identical")
        
        # Get status info
        status = self.run_git_command(['git', 'status', '--porcelain'], "Check working directory")
        if status.strip():
            logger.warning(f"Working directory has changes: {status}")
        
        # Get remote status
        remote_status = self.run_git_command(['git', 'status'], "Get detailed status")
        logger.info(f"Git Status: {remote_status}")
        
        logger.info("Current state verification completed")
        return {
            'current_branch': current_branch,
            'main_matches_initial': not bool(diff_result.strip()),
            'working_directory_clean': not bool(status.strip()),
            'remote_status': remote_status
        }
    
    def create_pre_push_backup(self):
        """Create backup of remote main before pushing"""
        logger.info("Creating pre-push backup reference...")
        
        # Create a backup reference to current remote main
        backup_ref = f"refs/backup/remote-main-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        self.run_git_command(['git', 'update-ref', backup_ref, 'origin/main'],
                           f"Create backup reference {backup_ref}")
        
        logger.info(f"Pre-push backup created: {backup_ref}")
        return backup_ref
    
    def execute_force_push(self):
        """Execute the force push with safety measures"""
        logger.info("Executing force push to remote...")
        
        # Use --force-with-lease for safer force push
        self.run_git_command(['git', 'push', 'origin', 'main', '--force-with-lease'],
                           "Force push main to remote with lease protection", 
                           check_output=False)
        
        logger.info("Force push completed successfully")
    
    def verify_push_success(self):
        """Verify that the push was successful"""
        logger.info("Verifying push success...")
        
        # Fetch latest remote state
        self.run_git_command(['git', 'fetch', 'origin'], "Fetch latest remote state")
        
        # Check that local main now matches remote main
        local_commit = self.run_git_command(['git', 'rev-parse', 'main'], "Get local main commit")
        remote_commit = self.run_git_command(['git', 'rev-parse', 'origin/main'], "Get remote main commit")
        
        if local_commit == remote_commit:
            logger.info("Push verification successful - local and remote main are in sync")
            return True
        else:
            logger.error(f"Push verification failed - commits differ:")
            logger.error(f"  Local main: {local_commit}")
            logger.error(f"  Remote main: {remote_commit}")
            return False
    
    def execute_push_workflow(self):
        """Execute the complete push workflow"""
        
        phases = [
            ("Verification", "Verifying current branch state", 20, self.verify_current_state),
            ("Backup", "Creating pre-push backup", 15, self.create_pre_push_backup),
            ("Push", "Executing force push to remote", 45, self.execute_force_push),
            ("Validation", "Verifying push success", 20, self.verify_push_success)
        ]
        
        results = {}
        
        with tqdm(total=100, desc="Branch Push", unit="%",
                 bar_format="{l_bar}{bar}| {n:.1f}/{total}{unit} [{elapsed}<{remaining}]") as pbar:
            
            for phase_name, phase_desc, weight, phase_func in phases:
                pbar.set_description(f"{phase_name}: {phase_desc}")
                
                try:
                    # Execute phase
                    result = phase_func()
                    results[phase_name] = result
                    
                    # Update progress
                    pbar.update(weight)
                    
                    # Log progress with timing
                    elapsed = (datetime.now() - self.start_time).total_seconds()
                    logger.info(f"Phase complete: {phase_name} | Elapsed: {elapsed:.1f}s")
                    
                except Exception as e:
                    logger.error(f"Phase failed: {phase_name} - {e}")
                    raise
        
        # MANDATORY: Completion summary
        self.log_completion_summary(results)
        return results
    
    def log_completion_summary(self, results):
        """MANDATORY: Log comprehensive completion summary"""
        duration = (datetime.now() - self.start_time).total_seconds()
        logger.info("="*60)
        logger.info("BRANCH PUSH EXECUTION COMPLETE")
        logger.info(f"Task: Push main branch (reset to initial) to remote")
        logger.info(f"Total Duration: {duration:.1f} seconds")
        logger.info(f"Process ID: {self.process_id}")
        logger.info(f"Completion Status: SUCCESS")
        
        # Log backup information
        if "Backup" in results:
            logger.info(f"Pre-push backup: {results['Backup']}")
        
        # Log verification status
        if "Validation" in results:
            logger.info(f"Push verification: {'PASSED' if results['Validation'] else 'FAILED'}")
        
        logger.info("="*60)

def main():
    """Main execution function with error handling"""
    try:
        # Initialize orchestrator
        orchestrator = BranchPushOrchestrator()
        
        # Execute push workflow
        results = orchestrator.execute_push_workflow()
        
        print("\n🎉 SUCCESS: Branch push completed successfully!")
        print("📁 Main branch (now matching initial) pushed to remote")
        print("🔄 Remote repository updated with initial branch content")
        if "Backup" in results:
            print(f"💾 Pre-push backup: {results['Backup']}")
        print("📋 Log file: branch_push.log")
        
        return 0
        
    except Exception as e:
        logger.error(f"BRANCH PUSH FAILED: {e}")
        print(f"\n❌ ERROR: {e}")
        print("📋 Check branch_push.log for details")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
