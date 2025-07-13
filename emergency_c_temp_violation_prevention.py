#!/usr/bin/env python3
"""
Emergency C:/Temp Violation Prevention System
Database-First Anti-Recursion Compliance Validator
"""
import argparse
import sys
import shutil
import logging
from pathlib import Path
from datetime import datetime

class EmergencyAntiRecursionValidator:
    """🚨 Emergency prevention of recursive folder creation and C:/temp violations"""
    
    def __init__(self):
        self.proper_root = Path("E:/gh_COPILOT")
        self.forbidden_patterns = ["--validate", "--backup", "--temp", "--target"]
        self.setup_logging()
        
    def setup_logging(self):
        """Setup enterprise logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def validate_workspace_integrity(self):
        """CRITICAL: Validate no recursive folder structures"""
        workspace_root = self.proper_root
        
        # Forbidden patterns that create recursion
        forbidden_patterns = ['*backup*', '*_backup_*', 'backups', '*temp*']
        violations = []
        
        for pattern in forbidden_patterns:
            for folder in workspace_root.rglob(pattern):
                if folder.is_dir() and folder != workspace_root:
                    violations.append(str(folder))
        
        if violations:
            for violation in violations:
                self.logger.error(f"🚨 RECURSIVE VIOLATION: {violation}")
                try:
                    shutil.rmtree(violation)  # Emergency removal
                    self.logger.info(f"✅ REMOVED RECURSIVE FOLDER: {violation}")
                except Exception as e:
                    self.logger.error(f"❌ FAILED TO REMOVE: {violation} - {e}")
            
        return len(violations) == 0
    
    def prevent_c_temp_violations(self):
        """🚨 EMERGENCY: Prevent unauthorized C:/temp/ usage"""
        c_temp_root = Path("C:/temp")
        violations = []
        
        # Only authorized: C:/temp/Auto_Build/...
        authorized_path = c_temp_root / "Auto_Build"
        
        if c_temp_root.exists():
            for item in c_temp_root.iterdir():
                if item.is_dir() and "gh_COPILOT" in item.name.upper():
                    if not str(item).startswith(str(authorized_path)):
                        violations.append(str(item))
                        self.logger.error(f"🚨 C:/temp/ VIOLATION: {item}")
                        try:
                            shutil.rmtree(item)
                            self.logger.info(f"✅ REMOVED VIOLATION: {item}")
                        except Exception as e:
                            self.logger.error(f"❌ FAILED TO REMOVE: {item} - {e}")
        
        return len(violations) == 0
    
    def emergency_cleanup(self):
        """🚨 EMERGENCY: Comprehensive anti-recursion cleanup"""
        self.logger.info("🚨 EMERGENCY ANTI-RECURSION CLEANUP INITIATED")
        
        # 1. Validate workspace integrity
        workspace_clean = self.validate_workspace_integrity()
        
        # 2. Prevent C:/temp violations
        c_temp_clean = self.prevent_c_temp_violations()
        
        # 3. Report results
        if workspace_clean and c_temp_clean:
            self.logger.info("✅ EMERGENCY CLEANUP: ALL CLEAR")
            return True
        else:
            self.logger.error("❌ EMERGENCY CLEANUP: VIOLATIONS DETECTED AND CLEANED")
            return False
    
    def full_validation(self):
        """Execute full validation protocol"""
        self.logger.info("🛡️ FULL ANTI-RECURSION VALIDATION INITIATED")
        
        start_time = datetime.now()
        
        # Execute comprehensive validation
        result = self.emergency_cleanup()
        
        duration = (datetime.now() - start_time).total_seconds()
        
        if result:
            self.logger.info(f"✅ FULL VALIDATION PASSED ({duration:.2f}s)")
            self.logger.info("🛡️ WORKSPACE ANTI-RECURSION COMPLIANCE: VERIFIED")
        else:
            self.logger.error(f"❌ FULL VALIDATION FAILED ({duration:.2f}s)")
            self.logger.error("🚨 WORKSPACE ANTI-RECURSION COMPLIANCE: VIOLATIONS FIXED")
        
        return result

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='Emergency Anti-Recursion Validation')
    parser.add_argument('--emergency-cleanup', action='store_true', 
                       help='Execute emergency cleanup')
    parser.add_argument('--full-validation', action='store_true',
                       help='Execute full validation protocol')
    
    args = parser.parse_args()
    
    validator = EmergencyAntiRecursionValidator()
    
    if args.emergency_cleanup:
        result = validator.emergency_cleanup()
        sys.exit(0 if result else 1)
    elif args.full_validation:
        result = validator.full_validation()
        sys.exit(0 if result else 1)
    else:
        # Default to full validation
        result = validator.full_validation()
        sys.exit(0 if result else 1)

if __name__ == "__main__":
    main()
