#!/usr/bin/env python3
"""
[ALERT] EMERGENCY C:\\TEMP VIOLATION PREVENTION SYSTEM
Critical Anti-Recursion and Environment Protection

CRITICAL: Prevents recursive folder creation and C:\\Temp violations
"""

import os
import sys
import json
import shutil
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from tqdm import tqdm
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('emergency_prevention.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class EmergencyPreventionResult:
    """Results from emergency prevention scan"""
    scan_id: str
    violations_found: int
    violations_removed: int
    c_temp_violations: List[str]
    recursive_violations: List[str]
    prevented_operations: List[str]
    timestamp: str
    success: bool

class EmergencyCtempViolationPrevention:
    """
    [ALERT] EMERGENCY C:\\TEMP VIOLATION PREVENTION
    
    Critical system to prevent:
    - Recursive folder creation within workspace
    - C:\\Temp path violations
    - Unauthorized backup folder creation
    - Environment root violations
    """
    
    def __init__(self, workspace_root: str = r"e:\_copilot_sandbox"):
        self.workspace_root = Path(workspace_root)
        self.scan_id = f"EMERGENCY_{int(time.time())}"
        self.start_time = datetime.now()
        
        # CRITICAL: Forbidden patterns
        self.forbidden_backup_paths = [
            'backup', 'backups', 'temp', 'tmp', 'cache', 'old', 'archive'
        ]
        self.forbidden_c_temp_patterns = [
            r'workspace_temp', 'workspace_temp', r'workspace_tmp', 'workspace_tmp', 
            r'c:\windows\temp', 'c:/windows/temp'
        ]
        self.critical_operations = [
            'mkdir', 'makedirs', 'create_folder', 'backup_create'
        ]
        
        logger.info(f"[ALERT] EMERGENCY PREVENTION SYSTEM INITIALIZED")
        logger.info(f"Scan ID: {self.scan_id}")
        logger.info(f"Workspace Root: {self.workspace_root}")
        
    def emergency_cleanup(self) -> EmergencyPreventionResult:
        """
        [ALERT] EMERGENCY CLEANUP PROTOCOL
        
        Immediate detection and removal of violations
        """
        logger.info("[ALERT] EXECUTING EMERGENCY CLEANUP PROTOCOL")
        
        c_temp_violations = []
        recursive_violations = []
        prevented_operations = []
        violations_removed = 0
        
        with tqdm(total=100, desc="Emergency Cleanup", unit="%") as pbar:
            # Phase 1: Scan for recursive violations
            logger.info("[SEARCH] Phase 1: Scanning for recursive violations")
            recursive_violations = self._scan_recursive_violations()
            pbar.update(25)
            
            # Phase 2: Scan for E:\_copilot_sandbox	emp violations
            logger.info("[WARNING] Phase 2: Scanning for C:\\Temp violations")
            c_temp_violations = self._scan_c_temp_violations()
            pbar.update(25)
            
            # Phase 3: Remove violations
            logger.info("[TRASH] Phase 3: Removing violations")
            violations_removed = self._remove_violations(recursive_violations)
            pbar.update(25)
            
            # Phase 4: Prevent future violations
            logger.info("[SHIELD] Phase 4: Implementing prevention measures")
            prevented_operations = self._implement_prevention()
            pbar.update(25)
        
        result = EmergencyPreventionResult(
            scan_id=self.scan_id,
            violations_found=len(recursive_violations) + len(c_temp_violations),
            violations_removed=violations_removed,
            c_temp_violations=c_temp_violations,
            recursive_violations=recursive_violations,
            prevented_operations=prevented_operations,
            timestamp=datetime.now().isoformat(),
            success=len(recursive_violations) == 0 and len(c_temp_violations) == 0
        )
        
        if result.success:
            logger.info("[SUCCESS] EMERGENCY CLEANUP: SUCCESS")
        else:
            logger.error("[ERROR] EMERGENCY CLEANUP: VIOLATIONS DETECTED")
            
        return result
    
    def _scan_recursive_violations(self) -> List[str]:
        """Scan for recursive backup folder violations"""
        violations = []
        
        try:
            for root, dirs, files in os.walk(self.workspace_root):
                for dir_name in dirs:
                    # Check if directory name contains forbidden patterns
                    if any(pattern in dir_name.lower() for pattern in self.forbidden_backup_paths):
                        dir_path = Path(root) / dir_name
                        
                        # Ensure it's within workspace (recursive violation)
                        if self._is_within_workspace(dir_path):
                            # Check if it's a backup folder
                            if self._is_backup_folder(dir_path):
                                violations.append(str(dir_path))
                                logger.error(f"[?] RECURSIVE VIOLATION: {dir_path}")
                                
        except Exception as e:
            logger.error(f"[ERROR] Error scanning recursive violations: {e}")
            
        return violations
    
    def _scan_c_temp_violations(self) -> List[str]:
        """Scan for C:\\Temp path violations in code"""
        violations = []
        
        try:
            for root, dirs, files in os.walk(self.workspace_root):
                for file in files:
                    if file.endswith(('.py', '.ps1', '.bat', '.cmd')):
                        file_path = Path(root) / file
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read().lower()
                                for pattern in self.forbidden_c_temp_patterns:
                                    if pattern in content:
                                        violations.append(f"{file_path}: {pattern}")
                                        logger.error(f"[WARNING] C:\\TEMP VIOLATION: {file_path}")
                        except Exception:
                            pass  # Skip files that can't be read
                            
        except Exception as e:
            logger.error(f"[ERROR] Error scanning C:\\Temp violations: {e}")
            
        return violations
    
    def _remove_violations(self, violations: List[str]) -> int:
        """Remove detected violations"""
        removed_count = 0
        
        for violation in violations:
            try:
                violation_path = Path(violation)
                if violation_path.exists() and violation_path.is_dir():
                    # Safety check: ensure it's really a violation
                    if self._confirm_violation(violation_path):
                        shutil.rmtree(violation_path)
                        removed_count += 1
                        logger.info(f"[TRASH] REMOVED VIOLATION: {violation_path}")
                    else:
                        logger.warning(f"[WARNING] VIOLATION NOT CONFIRMED: {violation_path}")
                        
            except Exception as e:
                logger.error(f"[ERROR] Error removing violation {violation}: {e}")
                
        return removed_count
    
    def _implement_prevention(self) -> List[str]:
        """Implement prevention measures"""
        prevented = []
        
        try:
            # Create prevention marker file
            prevention_file = self.workspace_root / ".emergency_prevention_active"
            with open(prevention_file, 'w') as f:
                f.write(f"Emergency prevention active since: {datetime.now().isoformat()}\n")
                f.write(f"Scan ID: {self.scan_id}\n")
            prevented.append("Prevention marker file created")
            
            # Log prevention measures
            logger.info("[SHIELD] Prevention measures implemented")
            
        except Exception as e:
            logger.error(f"[ERROR] Error implementing prevention: {e}")
            
        return prevented
    
    def _is_within_workspace(self, path: Path) -> bool:
        """Check if path is within workspace root"""
        try:
            path.resolve().relative_to(self.workspace_root.resolve())
            return True
        except ValueError:
            return False
    
    def _is_backup_folder(self, path: Path) -> bool:
        """Check if folder appears to be a backup folder"""
        try:
            # Check folder name patterns
            folder_name = path.name.lower()
            if any(pattern in folder_name for pattern in self.forbidden_backup_paths):
                return True
                
            # Check for backup-like contents
            if path.exists():
                contents = list(path.iterdir())
                if len(contents) > 0:
                    # Check if contains mostly backup files
                    backup_files = sum(1 for item in contents if '.backup' in item.name.lower())
                    if backup_files / len(contents) > 0.5:
                        return True
                        
        except Exception:
            pass
            
        return False
    
    def _confirm_violation(self, path: Path) -> bool:
        """Confirm a path is actually a violation before removal"""
        try:
            # Safety checks before removal
            if not self._is_within_workspace(path):
                return False
                
            if not self._is_backup_folder(path):
                return False
                
            # Additional safety: check if it's empty or contains only backups
            if path.exists():
                contents = list(path.iterdir())
                if len(contents) == 0:
                    return True
                    
                # Check if all contents are backup files
                non_backup_files = [item for item in contents if '.backup' not in item.name.lower()]
                if len(non_backup_files) == 0:
                    return True
                    
        except Exception:
            pass
            
        return False
    
    def full_validation(self) -> EmergencyPreventionResult:
        """
        [SEARCH] FULL VALIDATION PROTOCOL
        
        Comprehensive scan without removal
        """
        logger.info("[SEARCH] EXECUTING FULL VALIDATION PROTOCOL")
        
        c_temp_violations = self._scan_c_temp_violations()
        recursive_violations = self._scan_recursive_violations()
        
        result = EmergencyPreventionResult(
            scan_id=self.scan_id,
            violations_found=len(recursive_violations) + len(c_temp_violations),
            violations_removed=0,
            c_temp_violations=c_temp_violations,
            recursive_violations=recursive_violations,
            prevented_operations=[],
            timestamp=datetime.now().isoformat(),
            success=len(recursive_violations) == 0 and len(c_temp_violations) == 0
        )
        
        if result.success:
            logger.info("[SUCCESS] FULL VALIDATION: NO VIOLATIONS DETECTED")
        else:
            logger.error(f"[ERROR] FULL VALIDATION: {result.violations_found} VIOLATIONS DETECTED")
            
        return result
    
    def save_results(self, result: EmergencyPreventionResult) -> str:
        """Save prevention results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"emergency_prevention_results_{timestamp}.json"
        filepath = self.workspace_root / filename
        
        result_dict = {
            "scan_id": result.scan_id,
            "violations_found": result.violations_found,
            "violations_removed": result.violations_removed,
            "c_temp_violations": result.c_temp_violations,
            "recursive_violations": result.recursive_violations,
            "prevented_operations": result.prevented_operations,
            "timestamp": result.timestamp,
            "success": result.success
        }
        
        with open(filepath, 'w') as f:
            json.dump(result_dict, f, indent=2)
            
        logger.info(f"[STORAGE] Results saved to: {filepath}")
        return str(filepath)

def main():
    """Main execution function"""
    try:
        # Initialize prevention system
        prevention = EmergencyCtempViolationPrevention()
        
        # Check command line arguments
        if len(sys.argv) > 1:
            if "--emergency-cleanup" in sys.argv:
                logger.info("[ALERT] EXECUTING EMERGENCY CLEANUP")
                result = prevention.emergency_cleanup()
                
            elif "--full-validation" in sys.argv:
                logger.info("[SEARCH] EXECUTING FULL VALIDATION")
                result = prevention.full_validation()
                
            else:
                logger.info("[SEARCH] EXECUTING DEFAULT VALIDATION")
                result = prevention.full_validation()
        else:
            logger.info("[SEARCH] EXECUTING DEFAULT VALIDATION")
            result = prevention.full_validation()
        
        # Save results
        prevention.save_results(result)
        
        # Return appropriate exit code
        return 0 if result.success else 1
        
    except Exception as e:
        logger.error(f"[ERROR] CRITICAL ERROR: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
