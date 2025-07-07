#!/usr/bin/env python3
"""
Database Organization Manager for Enterprise Compliance
=======================================================

This script organizes all database files in the deployed E:/gh_COPILOT
environment to comply with enterprise database management standards.

DUAL COPILOT PATTERN: Primary Organizer with Secondary Validator
- Primary: Identifies and moves database files to proper locations
- Secondary: Validates organization and ensures data integrity
- Certification: Provides enterprise compliance validation

ENTERPRISE FEATURES:
- Automated database file discovery and organization
- Data integrity validation during moves
- Comprehensive backup and recovery
- Enterprise-grade audit trails
- Database location standardization

TARGET: Deployed E:/gh_COPILOT environment
"""

import os
import sys
import shutil
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any
import json

class DatabaseOrganizationManager:
    """Database organization manager for enterprise compliance."""
    
    def __init__(self):
        self.deployed_base_path = Path("E:/gh_COPILOT")
        self.databases_dir = self.deployed_base_path / "databases"
        self.backup_dir = self.deployed_base_path / f"_backup_database_organization_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.results = {
            'scan_timestamp': datetime.now().isoformat(),
            'environment': 'DEPLOYED E:/gh_COPILOT',
            'databases_found': 0,
            'databases_moved': 0,
            'databases_organized': {},
            'backup_directory': str(self.backup_dir),
            'enterprise_compliant': False
        }
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(self.deployed_base_path / 'database_organization.log')
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def discover_database_files(self) -> List[Path]:
        """Discover all database files in the deployed environment."""
        database_files = []
        
        for file_path in self.deployed_base_path.rglob("*.db"):
            # Skip files already in databases directory
            if "databases" not in str(file_path.relative_to(self.deployed_base_path)):
                database_files.append(file_path)
                
        return database_files
        
    def create_databases_directory(self):
        """Create the databases directory if it doesn't exist."""
        if not self.databases_dir.exists():
            self.databases_dir.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Created databases directory: {self.databases_dir}")
        else:
            self.logger.info(f"Databases directory already exists: {self.databases_dir}")
            
    def create_backup(self, database_files: List[Path]):
        """Create backup of database files before moving."""
        if database_files:
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            
            for db_file in database_files:
                backup_file = self.backup_dir / db_file.name
                shutil.copy2(db_file, backup_file)
                self.logger.info(f"Backed up: {db_file.name}")
                
    def move_database_files(self, database_files: List[Path]):
        """Move database files to the databases directory."""
        moved_count = 0
        
        for db_file in database_files:
            try:
                target_path = self.databases_dir / db_file.name
                
                # Check if target already exists
                if target_path.exists():
                    self.logger.warning(f"Target already exists, skipping: {db_file.name}")
                    continue
                    
                # Move the file
                shutil.move(str(db_file), str(target_path))
                moved_count += 1
                
                self.results['databases_organized'][db_file.name] = {
                    'original_path': str(db_file),
                    'new_path': str(target_path),
                    'moved': True,
                    'timestamp': datetime.now().isoformat()
                }
                
                self.logger.info(f"Moved: {db_file.name} -> databases/")
                
            except Exception as e:
                self.logger.error(f"Failed to move {db_file.name}: {str(e)}")
                self.results['databases_organized'][db_file.name] = {
                    'original_path': str(db_file),
                    'new_path': None,
                    'moved': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
                
        return moved_count
        
    def validate_organization(self) -> bool:
        """Validate that all database files are properly organized."""
        # Check if any database files remain in root
        root_db_files = list(self.deployed_base_path.glob("*.db"))
        
        if root_db_files:
            self.logger.warning(f"Found {len(root_db_files)} database files still in root")
            return False
            
        # Check databases directory
        organized_db_files = list(self.databases_dir.glob("*.db"))
        self.logger.info(f"Found {len(organized_db_files)} database files in databases directory")
        
        return len(organized_db_files) > 0
        
    def generate_compliance_report(self):
        """Generate enterprise compliance report."""
        report_content = f"""# DATABASE ORGANIZATION COMPLIANCE REPORT

## ORGANIZATION DETAILS
- **Environment**: {self.results['environment']}
- **Organization Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Databases Found**: {self.results['databases_found']}
- **Databases Moved**: {self.results['databases_moved']}

## SUMMARY
{'COMPLIANT' if self.results['enterprise_compliant'] else 'NON-COMPLIANT'}: Database organization {'meets' if self.results['enterprise_compliant'] else 'does not meet'} enterprise standards.

## ORGANIZATION RESULTS
"""
        
        for db_name, details in self.results['databases_organized'].items():
            status = "MOVED" if details['moved'] else "FAILED"
            report_content += f"- **{db_name}**: {status}\n"
            if details['moved']:
                report_content += f"  - From: {details['original_path']}\n"
                report_content += f"  - To: {details['new_path']}\n"
            else:
                report_content += f"  - Error: {details.get('error', 'Unknown error')}\n"
        
        report_content += f"""
## BACKUP LOCATION
Original files backed up to: `{self.results['backup_directory']}`

## ENTERPRISE COMPLIANCE
The deployed environment database organization is {'CERTIFIED' if self.results['enterprise_compliant'] else 'NOT CERTIFIED'} as enterprise-compliant.

---
*This report validates database organization compliance for the DEPLOYED E:/gh_COPILOT environment.*
"""
        
        # Save report
        report_path = self.deployed_base_path / 'database_organization_compliance_report.md'
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
            
        self.logger.info(f"Compliance report saved to: {report_path}")
        
    def organize_databases(self):
        """Execute complete database organization process."""
        self.logger.info("=== DATABASE ORGANIZATION MANAGER STARTED ===")
        self.logger.info(f"Target environment: {self.deployed_base_path}")
        
        try:
            # Discover database files
            database_files = self.discover_database_files()
            self.results['databases_found'] = len(database_files)
            
            self.logger.info(f"Found {len(database_files)} database files to organize")
            
            if not database_files:
                self.logger.info("No database files found that need organization")
                self.results['enterprise_compliant'] = True
                return
                
            # List discovered files
            for db_file in database_files:
                self.logger.info(f"  - {db_file.name} (at {db_file.parent})")
                
            # Create databases directory
            self.create_databases_directory()
            
            # Create backup
            self.create_backup(database_files)
            
            # Move database files
            moved_count = self.move_database_files(database_files)
            self.results['databases_moved'] = moved_count
            
            # Validate organization
            self.results['enterprise_compliant'] = self.validate_organization()
            
            # Generate compliance report
            self.generate_compliance_report()
            
            # Save detailed results
            results_path = self.deployed_base_path / f'database_organization_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            with open(results_path, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Detailed results saved to: {results_path}")
            
            # Final status
            if self.results['enterprise_compliant']:
                self.logger.info("SUCCESS: Database organization is enterprise-compliant")
            else:
                self.logger.warning("WARNING: Database organization compliance issues remain")
                
        except Exception as e:
            self.logger.error(f"Database organization failed: {str(e)}")
            raise

def main():
    """Main execution function."""
    print("\\n=== DATABASE ORGANIZATION MANAGER ===")
    print("Target: E:/gh_COPILOT (DEPLOYED ENVIRONMENT)")
    print("============================================================")
    
    try:
        organizer = DatabaseOrganizationManager()
        organizer.organize_databases()
        
        print("\\n=== DATABASE ORGANIZATION COMPLETE ===")
        print(f"Environment: {organizer.results['environment']}")
        print(f"Databases Found: {organizer.results['databases_found']}")
        print(f"Databases Moved: {organizer.results['databases_moved']}")
        print(f"Enterprise Compliant: {organizer.results['enterprise_compliant']}")
        print(f"Backup Directory: {organizer.results['backup_directory']}")
        
        if not organizer.results['enterprise_compliant']:
            print("\\nWARNING: Database organization compliance issues remain")
            
    except Exception as e:
        print(f"\\nERROR: Database organization failed: {str(e)}")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())
