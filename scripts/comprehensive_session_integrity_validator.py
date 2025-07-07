#!/usr/bin/env python3
"""
[SHIELD] COMPREHENSIVE SESSION INTEGRITY VALIDATOR
GitHub Copilot Zero-Byte Protection & System Validation Framework

CRITICAL: Implements mandatory session protocols per COMPREHENSIVE_SESSION_INTEGRITY.instructions.md
"""

import os
import sys
import json
import sqlite3
import hashlib
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
        logging.FileHandler('session_integrity_validation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class SessionIntegrityResult:
    """Results from session integrity validation"""
    session_id: str
    validation_passed: bool
    zero_byte_files: List[str]
    recursive_violations: List[str]
    c_temp_violations: List[str]
    database_issues: List[str]
    workspace_issues: List[str]
    timestamp: str
    summary: Dict[str, Any]

class ComprehensiveSessionIntegrityValidator:
    """
    [SHIELD] COMPREHENSIVE SESSION INTEGRITY VALIDATOR
    
    Implements mandatory session protocols:
    - Zero-byte file prevention
    - Anti-recursion validation
    - Database integrity checks
    - Workspace validation
    - Emergency cleanup
    """
    
    def __init__(self, workspace_root: str = r"e:\_copilot_sandbox"):
        self.workspace_root = Path(workspace_root)
        self.session_id = f"SESSION_{int(time.time())}"
        self.start_time = datetime.now()
        
        # CRITICAL: Protected paths and patterns
        self.protected_extensions = {'.py', '.ps1', '.md', '.json', '.db', '.sqlite', '.js', '.html', '.css'}
        self.forbidden_backup_patterns = ['backup', 'temp', 'tmp', 'cache']
        self.forbidden_c_temp_patterns = [r'workspace_temp', 'workspace_temp', r'workspace_tmp', 'workspace_tmp']
        
        logger.info(f"[LAUNCH] SESSION INTEGRITY VALIDATOR INITIALIZED")
        logger.info(f"Session ID: {self.session_id}")
        logger.info(f"Workspace Root: {self.workspace_root}")
        logger.info(f"Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
    def validate_session_startup(self) -> SessionIntegrityResult:
        """
        [SHIELD] MANDATORY SESSION STARTUP PROTOCOL
        
        Implements comprehensive validation before any work begins
        """
        logger.info("[SEARCH] EXECUTING SESSION STARTUP PROTOCOL")
        
        zero_byte_files = []
        recursive_violations = []
        c_temp_violations = []
        database_issues = []
        workspace_issues = []
        
        with tqdm(total=100, desc="Session Startup Validation", unit="%") as pbar:
            # Phase 1: Zero-byte file scan
            logger.info("[BAR_CHART] Phase 1: Zero-byte file detection")
            zero_byte_files = self._scan_zero_byte_files()
            pbar.update(20)
            
            # Phase 2: Anti-recursion validation
            logger.info("[?] Phase 2: Anti-recursion validation")
            recursive_violations = self._validate_anti_recursion()
            pbar.update(20)
            
            # Phase 3: E:\_copilot_sandbox	emp violation check
            logger.info("[WARNING] Phase 3: C:\\Temp violation detection")
            c_temp_violations = self._check_c_temp_violations()
            pbar.update(20)
            
            # Phase 4: Database integrity check
            logger.info("[FILE_CABINET] Phase 4: Database integrity validation")
            database_issues = self._validate_database_integrity()
            pbar.update(20)
            
            # Phase 5: Workspace validation
            logger.info("[FOLDER] Phase 5: Workspace structure validation")
            workspace_issues = self._validate_workspace_structure()
            pbar.update(20)
            
        # Determine validation status
        validation_passed = (
            len(zero_byte_files) == 0 and
            len(recursive_violations) == 0 and
            len(c_temp_violations) == 0 and
            len(database_issues) == 0 and
            len(workspace_issues) == 0
        )
        
        result = SessionIntegrityResult(
            session_id=self.session_id,
            validation_passed=validation_passed,
            zero_byte_files=zero_byte_files,
            recursive_violations=recursive_violations,
            c_temp_violations=c_temp_violations,
            database_issues=database_issues,
            workspace_issues=workspace_issues,
            timestamp=datetime.now().isoformat(),
            summary={
                "total_issues": len(zero_byte_files) + len(recursive_violations) + len(c_temp_violations) + len(database_issues) + len(workspace_issues),
                "zero_byte_count": len(zero_byte_files),
                "recursive_violation_count": len(recursive_violations),
                "c_temp_violation_count": len(c_temp_violations),
                "database_issue_count": len(database_issues),
                "workspace_issue_count": len(workspace_issues)
            }
        )
        
        if validation_passed:
            logger.info("[SUCCESS] SESSION STARTUP VALIDATION: PASSED")
        else:
            logger.error("[ERROR] SESSION STARTUP VALIDATION: FAILED")
            logger.error(f"Total Issues: {result.summary['total_issues']}")
            
        return result
    
    def _scan_zero_byte_files(self) -> List[str]:
        """Scan for zero-byte files"""
        zero_byte_files = []
        
        try:
            for root, dirs, files in os.walk(self.workspace_root):
                for file in files:
                    file_path = Path(root) / file
                    if file_path.stat().st_size == 0:
                        zero_byte_files.append(str(file_path))
                        logger.warning(f"[WARNING] Zero-byte file detected: {file_path}")
        except Exception as e:
            logger.error(f"[ERROR] Error scanning zero-byte files: {e}")
            
        return zero_byte_files
    
    def _validate_anti_recursion(self) -> List[str]:
        """Validate anti-recursion rules"""
        violations = []
        
        try:
            for root, dirs, files in os.walk(self.workspace_root):
                # Check for forbidden backup folders within workspace
                for dir_name in dirs:
                    if any(pattern in dir_name.lower() for pattern in self.forbidden_backup_patterns):
                        full_path = Path(root) / dir_name
                        if self._is_within_workspace(full_path):
                            violations.append(f"Recursive backup folder: {full_path}")
                            logger.error(f"[?] RECURSIVE VIOLATION: {full_path}")
        except Exception as e:
            logger.error(f"[ERROR] Error validating anti-recursion: {e}")
            
        return violations
    
    def _check_c_temp_violations(self) -> List[str]:
        """Check for C:\\Temp violations"""
        violations = []
        
        try:
            # Check for any references to E:\_copilot_sandbox	emp in files
            for root, dirs, files in os.walk(self.workspace_root):
                for file in files:
                    if file.endswith('.py'):
                        file_path = Path(root) / file
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read().lower()
                                for pattern in self.forbidden_c_temp_patterns:
                                    if pattern in content:
                                        violations.append(f"C:\\Temp reference in {file_path}")
                                        logger.error(f"[WARNING] C:\\TEMP VIOLATION: {file_path}")
                        except Exception:
                            pass  # Skip files that can't be read
        except Exception as e:
            logger.error(f"[ERROR] Error checking C:\\Temp violations: {e}")
            
        return violations
    
    def _validate_database_integrity(self) -> List[str]:
        """Validate database integrity"""
        issues = []
        
        try:
            databases_dir = self.workspace_root / "databases"
            if databases_dir.exists():
                for db_file in databases_dir.glob("*.db"):
                    try:
                        with sqlite3.connect(str(db_file)) as conn:
                            cursor = conn.cursor()
                            cursor.execute("PRAGMA integrity_check;")
                            result = cursor.fetchone()
                            if result[0] != "ok":
                                issues.append(f"Database corruption: {db_file}")
                                logger.error(f"[FILE_CABINET] DATABASE ISSUE: {db_file}")
                    except Exception as e:
                        issues.append(f"Database access error: {db_file} - {e}")
                        logger.error(f"[FILE_CABINET] DATABASE ERROR: {db_file} - {e}")
        except Exception as e:
            logger.error(f"[ERROR] Error validating database integrity: {e}")
            
        return issues
    
    def _validate_workspace_structure(self) -> List[str]:
        """Validate workspace structure"""
        issues = []
        
        try:
            # Check for required directories
            required_dirs = ['databases', 'generated_scripts']
            for dir_name in required_dirs:
                dir_path = self.workspace_root / dir_name
                if not dir_path.exists():
                    issues.append(f"Missing required directory: {dir_name}")
                    logger.warning(f"[FOLDER] MISSING DIRECTORY: {dir_name}")
                    
            # Check for critical files
            critical_files = ['master_framework_orchestrator.py', 'step1_factory_deployment.py']
            for file_name in critical_files:
                file_path = self.workspace_root / file_name
                if not file_path.exists():
                    issues.append(f"Missing critical file: {file_name}")
                    logger.warning(f"[?] MISSING FILE: {file_name}")
        except Exception as e:
            logger.error(f"[ERROR] Error validating workspace structure: {e}")
            
        return issues
    
    def _is_within_workspace(self, path: Path) -> bool:
        """Check if path is within workspace root"""
        try:
            path.resolve().relative_to(self.workspace_root.resolve())
            return True
        except ValueError:
            return False
    
    def emergency_cleanup(self) -> Dict[str, Any]:
        """
        [ALERT] EMERGENCY CLEANUP PROTOCOL
        
        Removes recursive violations and fixes critical issues
        """
        logger.info("[ALERT] EXECUTING EMERGENCY CLEANUP PROTOCOL")
        
        cleanup_results = {
            "zero_byte_recovered": 0,
            "recursive_violations_removed": 0,
            "c_temp_violations_fixed": 0,
            "database_issues_resolved": 0,
            "total_actions": 0
        }
        
        with tqdm(total=100, desc="Emergency Cleanup", unit="%") as pbar:
            # Phase 1: Remove recursive violations
            logger.info("[?] Phase 1: Removing recursive violations")
            violations = self._validate_anti_recursion()
            for violation in violations:
                try:
                    if "Recursive backup folder:" in violation:
                        folder_path = violation.split(": ")[1]
                        if os.path.exists(folder_path):
                            shutil.rmtree(folder_path)
                            cleanup_results["recursive_violations_removed"] += 1
                            logger.info(f"[TRASH] Removed recursive folder: {folder_path}")
                except Exception as e:
                    logger.error(f"[ERROR] Error removing recursive violation: {e}")
            pbar.update(50)
            
            # Phase 2: Database recovery
            logger.info("[FILE_CABINET] Phase 2: Database recovery")
            # Note: Database recovery would be implemented here
            pbar.update(50)
            
        cleanup_results["total_actions"] = (
            cleanup_results["zero_byte_recovered"] +
            cleanup_results["recursive_violations_removed"] +
            cleanup_results["c_temp_violations_fixed"] +
            cleanup_results["database_issues_resolved"]
        )
        
        logger.info(f"[SUCCESS] EMERGENCY CLEANUP COMPLETE: {cleanup_results['total_actions']} actions taken")
        return cleanup_results
    
    def validate_session_end(self) -> SessionIntegrityResult:
        """
        [SHIELD] MANDATORY SESSION END PROTOCOL
        
        Final validation before session termination
        """
        logger.info("[SEARCH] EXECUTING SESSION END PROTOCOL")
        
        # Run full validation again
        result = self.validate_session_startup()
        
        # Additional session end checks
        end_time = datetime.now()
        session_duration = end_time - self.start_time
        
        result.summary["session_duration_seconds"] = session_duration.total_seconds()
        result.summary["session_end_time"] = end_time.isoformat()
        
        if result.validation_passed:
            logger.info("[SUCCESS] SESSION END VALIDATION: PASSED")
        else:
            logger.error("[ERROR] SESSION END VALIDATION: FAILED")
            
        return result
    
    def save_results(self, result: SessionIntegrityResult) -> str:
        """Save validation results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"session_integrity_validation_{timestamp}.json"
        filepath = self.workspace_root / filename
        
        result_dict = {
            "session_id": result.session_id,
            "validation_passed": result.validation_passed,
            "zero_byte_files": result.zero_byte_files,
            "recursive_violations": result.recursive_violations,
            "c_temp_violations": result.c_temp_violations,
            "database_issues": result.database_issues,
            "workspace_issues": result.workspace_issues,
            "timestamp": result.timestamp,
            "summary": result.summary
        }
        
        with open(filepath, 'w') as f:
            json.dump(result_dict, f, indent=2)
            
        logger.info(f"[STORAGE] Results saved to: {filepath}")
        return str(filepath)

def main():
    """Main execution function"""
    try:
        # Initialize validator
        validator = ComprehensiveSessionIntegrityValidator()
        
        # Check command line arguments
        if len(sys.argv) > 1:
            if "--session-start" in sys.argv:
                logger.info("[LAUNCH] EXECUTING SESSION START PROTOCOL")
                result = validator.validate_session_startup()
                
            elif "--session-end" in sys.argv:
                logger.info("[?] EXECUTING SESSION END PROTOCOL")
                result = validator.validate_session_end()
                
            elif "--emergency-cleanup" in sys.argv:
                logger.info("[ALERT] EXECUTING EMERGENCY CLEANUP")
                cleanup_results = validator.emergency_cleanup()
                result = validator.validate_session_startup()
                
            elif "--full-validation" in sys.argv:
                logger.info("[SEARCH] EXECUTING FULL VALIDATION")
                result = validator.validate_session_startup()
                
            else:
                logger.info("[SEARCH] EXECUTING DEFAULT SESSION VALIDATION")
                result = validator.validate_session_startup()
        else:
            logger.info("[SEARCH] EXECUTING DEFAULT SESSION VALIDATION")
            result = validator.validate_session_startup()
        
        # Save results
        validator.save_results(result)
        
        # Return appropriate exit code
        return 0 if result.validation_passed else 1
        
    except Exception as e:
        logger.error(f"[ERROR] CRITICAL ERROR: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
