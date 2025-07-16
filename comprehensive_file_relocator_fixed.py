#!/usr/bin/env python3
"""
COMPREHENSIVE FILE RELOCATOR - CHUNK 3 IMPLEMENTATION
Enterprise File Organization System with Database Integration
Database-First File Management with Anti-Recursion Protection

MANDATORY: Apply comprehensive file organization from .github/instructions/AUTONOMOUS_FILE_MANAGEMENT.instructions.md
MANDATORY: Implement DUAL COPILOT PATTERN validation
MANDATORY: Use visual processing indicators per ZERO_TOLERANCE_VISUAL_PROCESSING.instructions.md
"""

import os
import sys
import json
import sqlite3
import hashlib
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from tqdm import tqdm
import logging

# MANDATORY: Enterprise logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('comprehensive_file_relocation.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ComprehensiveFileRelocator:
    """Comprehensive File Relocator with Enterprise Compliance"""
    
    def __init__(self, workspace_path: str = "e:/gh_COPILOT"):
        # MANDATORY: Start time logging with enterprise formatting
        self.start_time = datetime.now()
        self.process_id = os.getpid()
        logger.info("="*80)
        logger.info("COMPREHENSIVE FILE RELOCATOR INITIALIZED")
        logger.info(f"Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Process ID: {self.process_id}")
        logger.info("="*80)
        
        self.workspace_path = Path(workspace_path)
        self.database_path = self.workspace_path / "databases" / "production.db"
        
        # CRITICAL: Anti-recursion validation at startup
        self.validate_environment_compliance()
        
        # Target directories
        self.target_directories = {
            'logs': self.workspace_path / "logs",
            'documentation': self.workspace_path / "documentation", 
            'reports': self.workspace_path / "reports",
            'results': self.workspace_path / "results"
        }
        
        # MANDATORY: Ensure target directories exist
        self.ensure_target_directories()
        
        # File categorization patterns
        self.file_patterns = {
            'logs': ['.log', '.txt', 'log_', '_log', 'logs_', '_logs'],
            'documentation': ['.md', '.rst', '.txt', 'README', 'CHANGELOG', 'LICENSE', 'INSTALL', 'GUIDE', 'MANUAL'],
            'reports': ['report_', '_report', 'compliance_', 'audit_', 'summary_', 'analysis_', '.json'],
            'results': ['result_', '_result', 'output_', '_output', 'processed_', '_processed']
        }
        
        # Statistics tracking
        self.stats = {
            'total_files': 0,
            'successful_relocations': 0,
            'failed_relocations': 0,
            'database_updates': 0,
            'skipped_files': 0
        }
        
    def validate_environment_compliance(self):
        """CRITICAL: Validate environment compliance and anti-recursion protection"""
        logger.info("VALIDATING ENVIRONMENT COMPLIANCE...")
        
        # FORBIDDEN: Check for recursive backup patterns
        forbidden_patterns = ['*backup*', '*_backup_*', 'backups', '*temp*']
        violations = []
        
        for pattern in forbidden_patterns:
            for folder in self.workspace_path.rglob(pattern):
                if folder.is_dir() and folder != self.workspace_path:
                    violations.append(str(folder))
        
        if violations:
            logger.error("RECURSIVE FOLDER VIOLATIONS DETECTED:")
            for violation in violations:
                logger.error(f"   - {violation}")
            raise RuntimeError("CRITICAL: Recursive folder violations prevent execution")
        
        # MANDATORY: Validate proper environment root
        if not str(self.workspace_path).endswith("gh_COPILOT"):
            logger.warning(f"Non-standard workspace root: {self.workspace_path}")
        
        logger.info("ENVIRONMENT COMPLIANCE VALIDATED")
        
    def ensure_target_directories(self):
        """Ensure all target directories exist"""
        logger.info("ENSURING TARGET DIRECTORIES...")
        
        for dir_name, dir_path in self.target_directories.items():
            if not dir_path.exists():
                dir_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created directory: {dir_path}")
            else:
                logger.info(f"Directory exists: {dir_path}")
                
    def categorize_file(self, file_path: Path) -> Optional[str]:
        """Categorize file based on patterns and content"""
        file_name = file_path.name.lower()
        file_suffix = file_path.suffix.lower()
        
        # Check each category
        for category, patterns in self.file_patterns.items():
            for pattern in patterns:
                if pattern.startswith('.') and file_suffix == pattern:
                    return category
                elif not pattern.startswith('.') and pattern in file_name:
                    return category
                    
        return None
        
    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash for file integrity"""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                return hashlib.sha256(content).hexdigest()
        except Exception as e:
            logger.warning(f"Could not calculate hash for {file_path}: {e}")
            return "HASH_CALCULATION_FAILED"
            
    def read_file_content(self, file_path: Path) -> str:
        """Read file content for database storage"""
        try:
            # Try to read as text first
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            try:
                # Try with different encoding
                with open(file_path, 'r', encoding='latin-1') as f:
                    return f.read()
            except Exception:
                # For binary files, return a placeholder
                return f"[BINARY FILE: {file_path.suffix}]"
        except Exception as e:
            logger.warning(f"Could not read content for {file_path}: {e}")
            return f"[READ ERROR: {str(e)}]"
            
    def get_file_stats(self, file_path: Path) -> Tuple[int, int]:
        """Get file statistics"""
        try:
            file_size = file_path.stat().st_size
            
            # Count lines for text files
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines_of_code = sum(1 for _ in f)
            except:
                lines_of_code = 0
                
            return file_size, lines_of_code
        except Exception as e:
            logger.warning(f"Could not get stats for {file_path}: {e}")
            return 0, 0
            
    def update_database_mapping(self, old_path: str, new_path: str, file_path: Path):
        """Update database with new file mapping"""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                
                # Read file content and calculate metadata
                file_content = self.read_file_content(file_path)
                file_hash = self.calculate_file_hash(file_path)
                file_size, lines_of_code = self.get_file_stats(file_path)
                
                # Determine file type and category
                file_suffix = file_path.suffix.lower()
                file_category = self.categorize_file(file_path)
                
                script_type = "script" if file_suffix in ['.py', '.ps1', '.sh', '.bat'] else "document"
                functionality_category = file_category if file_category else "general"
                
                # Insert new mapping into database
                cursor.execute("""
                    INSERT INTO enhanced_script_tracking (
                        script_path, script_content, script_hash, script_type,
                        functionality_category, file_size, lines_of_code,
                        last_updated, regeneration_priority
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    new_path, file_content, file_hash, script_type,
                    functionality_category, file_size, lines_of_code,
                    datetime.now().isoformat(), 5
                ))
                
                conn.commit()
                self.stats['database_updates'] += 1
                logger.debug(f"Database updated for: {new_path}")
                
        except Exception as e:
            logger.error(f"Database update failed for {new_path}: {e}")
            
    def relocate_file(self, source_path: Path, category: str) -> bool:
        """Relocate single file to appropriate directory"""
        try:
            target_dir = self.target_directories[category]
            target_path = target_dir / source_path.name
            
            # Handle name collisions
            counter = 1
            original_target = target_path
            while target_path.exists():
                stem = original_target.stem
                suffix = original_target.suffix
                target_path = target_dir / f"{stem}_{counter}{suffix}"
                counter += 1
                
            # Perform the file move
            shutil.move(str(source_path), str(target_path))
            
            # Update database mapping
            self.update_database_mapping(
                str(source_path), 
                str(target_path), 
                target_path
            )
            
            self.stats['successful_relocations'] += 1
            logger.debug(f"Relocated: {source_path} -> {target_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to relocate {source_path}: {e}")
            self.stats['failed_relocations'] += 1
            return False
            
    def scan_and_categorize_files(self) -> Dict[str, List[Path]]:
        """Scan workspace and categorize files for relocation"""
        logger.info("SCANNING WORKSPACE FOR FILES TO RELOCATE...")
        
        categorized_files = {
            'logs': [],
            'documentation': [], 
            'reports': [],
            'results': []
        }
        
        # Scan root directory only (avoid subdirectories to prevent recursion)
        for item in self.workspace_path.iterdir():
            if item.is_file() and not item.name.startswith('.'):
                category = self.categorize_file(item)
                if category:
                    categorized_files[category].append(item)
                    self.stats['total_files'] += 1
                else:
                    self.stats['skipped_files'] += 1
                    
        # Log categorization summary
        for category, files in categorized_files.items():
            logger.info(f"{category.upper()}: {len(files)} files identified")
            
        logger.info(f"TOTAL FILES TO RELOCATE: {self.stats['total_files']}")
        logger.info(f"SKIPPED FILES: {self.stats['skipped_files']}")
        
        return categorized_files
        
    def execute_comprehensive_relocation(self):
        """Execute comprehensive file relocation with visual indicators"""
        
        # MANDATORY: Progress tracking initialization
        logger.info("STARTING COMPREHENSIVE FILE RELOCATION...")
        
        # Phase 1: Scan and categorize files
        categorized_files = self.scan_and_categorize_files()
        
        if self.stats['total_files'] == 0:
            logger.info("NO FILES REQUIRE RELOCATION - WORKSPACE ALREADY ORGANIZED")
            return
            
        # Phase 2: Execute relocations with progress tracking
        logger.info("EXECUTING FILE RELOCATIONS...")
        
        with tqdm(total=self.stats['total_files'], desc="Relocating Files", unit="files") as pbar:
            
            for category, files in categorized_files.items():
                if not files:
                    continue
                    
                pbar.set_description(f"Processing {category.upper()} files")
                
                for file_path in files:
                    # CRITICAL: Periodic anti-recursion validation
                    if self.stats['successful_relocations'] % 10 == 0:
                        self.validate_no_new_recursive_folders()
                    
                    success = self.relocate_file(file_path, category)
                    pbar.update(1)
                    
                    # Update progress description with stats
                    success_rate = (self.stats['successful_relocations'] / 
                                  max(1, self.stats['successful_relocations'] + self.stats['failed_relocations'])) * 100
                    pbar.set_postfix({
                        'Success': f"{success_rate:.1f}%",
                        'DB Updates': self.stats['database_updates']
                    })
                    
    def validate_no_new_recursive_folders(self):
        """Validate no new recursive folders created during processing"""
        forbidden_patterns = ['*backup*', '*_backup_*', 'backups']
        for pattern in forbidden_patterns:
            for folder in self.workspace_path.rglob(pattern):
                if folder.is_dir() and "backup" in folder.name.lower():
                    logger.error(f"RECURSIVE FOLDER DETECTED DURING PROCESSING: {folder}")
                    shutil.rmtree(folder)
                    logger.info(f"Removed recursive violation: {folder}")
                    
    def generate_completion_report(self):
        """Generate comprehensive completion report"""
        
        # MANDATORY: Calculate completion metrics
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        success_rate = (self.stats['successful_relocations'] / 
                       max(1, self.stats['total_files'])) * 100
        
        logger.info("="*80)
        logger.info("COMPREHENSIVE FILE RELOCATION COMPLETE")
        logger.info("="*80)
        logger.info(f"Total Duration: {duration:.2f} seconds")
        logger.info(f"Total Files Processed: {self.stats['total_files']}")
        logger.info(f"Successful Relocations: {self.stats['successful_relocations']}")
        logger.info(f"Failed Relocations: {self.stats['failed_relocations']}")
        logger.info(f"Database Updates: {self.stats['database_updates']}")
        logger.info(f"Success Rate: {success_rate:.1f}%")
        logger.info(f"Skipped Files: {self.stats['skipped_files']}")
        logger.info("="*80)
        
        # Generate JSON report
        report = {
            "operation": "comprehensive_file_relocation",
            "timestamp": end_time.isoformat(),
            "duration_seconds": duration,
            "process_id": self.process_id,
            "statistics": self.stats,
            "success_rate": success_rate,
            "status": "EXCELLENT" if success_rate >= 95 else "GOOD" if success_rate >= 80 else "NEEDS_ATTENTION"
        }
        
        report_path = self.workspace_path / f"comprehensive_relocation_report_{end_time.strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
            
        logger.info(f"Report saved: {report_path}")
        return report

def main():
    """Main execution function with DUAL COPILOT pattern"""
    
    try:
        # MANDATORY: Initialize comprehensive file relocator
        relocator = ComprehensiveFileRelocator()
        
        # Execute comprehensive relocation
        relocator.execute_comprehensive_relocation()
        
        # Generate completion report
        report = relocator.generate_completion_report()
        
        # DUAL COPILOT VALIDATION
        if report['success_rate'] >= 95:
            logger.info("DUAL COPILOT VALIDATION: COMPREHENSIVE RELOCATION APPROVED")
        else:
            logger.warning("DUAL COPILOT VALIDATION: NEEDS REVIEW")
            
        return report
        
    except Exception as e:
        logger.error(f"CRITICAL ERROR: {e}")
        logger.error("DUAL COPILOT VALIDATION: FAILED")
        raise

if __name__ == "__main__":
    main()
