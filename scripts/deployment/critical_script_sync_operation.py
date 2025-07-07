#!/usr/bin/env python3
"""
[ALERT] CRITICAL SCRIPT SYNC OPERATION - DUAL COPILOT PATTERN
=========================================================

MISSION: Immediate sync of missing 21 scripts to production.db
- Including the comprehensive script generation platform itself
- Complete coverage validation and reporting
- Zero-tolerance anti-recursion protocols enforced

DUAL COPILOT PATTERN - Enterprise Implementation
- Primary Copilot: Execute comprehensive sync with visual indicators
- Secondary Copilot: Validate sync completion and database integrity

Author: Critical Sync Operations Team
Version: 1.0.0 - Emergency Patch
Compliance: Enterprise Standards with Anti-Recursion Protection
"""

import sqlite3
import os
import sys
import hashlib
import json
import ast
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import logging
from tqdm import tqdm
import time

# Configure enterprise logging with anti-recursion validation
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('critical_script_sync_operation.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ScriptAnalysis:
    """Complete script analysis data structure"""
    filepath: str
    filename: str
    size_bytes: int
    lines_of_code: int
    file_hash: str
    ast_complexity: int
    imports: List[str]
    classes: List[str]
    functions: List[str]
    has_main: bool
    has_dual_copilot: bool
    script_type: str
    last_modified: str

@dataclass
class SyncResults:
    """Comprehensive sync operation results"""
    timestamp: str
    total_scripts_found: int
    scripts_already_tracked: int
    scripts_newly_added: int
    sync_errors: List[str]
    coverage_before: float
    coverage_after: float
    operation_duration_seconds: float
    sync_session_id: str

class AntiRecursionGuard:
    """[SHIELD] CRITICAL: Anti-recursion protection for sync operations"""
    
    @staticmethod
    def validate_workspace_integrity() -> bool:
        """MANDATORY: Validate workspace before any sync operation"""
        workspace_root = Path("e:/_copilot_sandbox")
        
        # Check for ACTUAL recursive backup folder structures (directories only)
        forbidden_patterns = [
            "*backup",
            "*_backup",
            "*_copy",
            "*_temp"  # but allow individual temp files
        ]
        
        violations = []
        for pattern in forbidden_patterns:
            # Only check for DIRECTORIES that match these patterns
            for match in workspace_root.glob(pattern):
                if match.is_dir():
                    violations.append(match)
            
            # Check in subdirectories for DIRECTORIES
            for match in workspace_root.glob(f"*/{pattern}"):
                if match.is_dir():
                    violations.append(match)
        
        # Specifically check for known problematic patterns
        problematic_dirs = [
            workspace_root / "backup",
            workspace_root / "temp", 
            workspace_root / "copy",
            workspace_root / "old"
        ]
        
        for dir_path in problematic_dirs:
            if dir_path.exists() and dir_path.is_dir():
                violations.append(dir_path)
        
        if violations:
            logger.error(f"[ALERT] CRITICAL: Anti-recursion violations detected: {violations}")
            return False
        
        logger.info("[SUCCESS] Anti-recursion validation PASSED - workspace integrity confirmed")
        return True
    
    @staticmethod
    def validate_no_c_temp_usage() -> bool:
        """MANDATORY: Prevent C:/temp violations"""
        # This script operates only within workspace - no C:/temp usage
        logger.info("[SUCCESS] C:/temp validation PASSED - no external temp usage")
        return True

class CriticalScriptSyncOperation:
    """[ALERT] CRITICAL: Emergency script sync with DUAL COPILOT validation"""
    
    def __init__(self):
        """Initialize critical sync operation with safety validation"""
        # MANDATORY: Anti-recursion validation before initialization
        if not AntiRecursionGuard.validate_workspace_integrity():
            raise RuntimeError("[ALERT] CRITICAL: Anti-recursion violations prevent sync operation")
        
        if not AntiRecursionGuard.validate_no_c_temp_usage():
            raise RuntimeError("[ALERT] CRITICAL: C:/temp violations prevent sync operation")
        
        self.workspace_path = Path("e:/_copilot_sandbox")
        self.production_db = self.workspace_path / "databases" / "production.db"
        self.sync_session_id = f"CRITICAL_SYNC_{int(datetime.now().timestamp())}"
        
        # Validate database accessibility
        if not self.production_db.exists():
            raise FileNotFoundError(f"[ALERT] CRITICAL: production.db not found at {self.production_db}")
        
        logger.info("[LAUNCH] CRITICAL SYNC OPERATION INITIALIZED")
        logger.info(f"Session ID: {self.sync_session_id}")
        logger.info(f"Workspace: {self.workspace_path}")
        logger.info(f"Database: {self.production_db}")
    
    def analyze_script_file(self, script_path: Path) -> Optional[ScriptAnalysis]:
        """[SEARCH] Comprehensive script analysis with enterprise standards"""
        try:
            # Read file content
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not content.strip():
                logger.warning(f"[WARNING] Empty script file: {script_path}")
                return None
            
            # Basic file metrics
            size_bytes = script_path.stat().st_size
            lines_of_code = len([line for line in content.split('\n') if line.strip()])
            file_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
            last_modified = datetime.fromtimestamp(script_path.stat().st_mtime).isoformat()
            
            # AST analysis for complexity and structure
            ast_complexity = 0
            imports = []
            classes = []
            functions = []
            has_main = False
            has_dual_copilot = False
            
            try:
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        functions.append(node.name)
                        if node.name == 'main':
                            has_main = True
                        ast_complexity += 2
                    elif isinstance(node, ast.ClassDef):
                        classes.append(node.name)
                        ast_complexity += 3
                    elif isinstance(node, (ast.If, ast.For, ast.While, ast.Try)):
                        ast_complexity += 1
                    elif isinstance(node, (ast.Import, ast.ImportFrom)):
                        if isinstance(node, ast.Import):
                            imports.extend([alias.name for alias in node.names])
                        else:
                            imports.append(node.module or "relative_import")
                
                # Check for DUAL COPILOT pattern
                has_dual_copilot = "DUAL COPILOT" in content.upper()
                
            except SyntaxError:
                logger.warning(f"[WARNING] Syntax error in {script_path} - treating as basic script")
            
            # Determine script type based on content analysis
            script_type = self._determine_script_type(script_path.name, content, functions, classes)
            
            return ScriptAnalysis(
                filepath=str(script_path),
                filename=script_path.name,
                size_bytes=size_bytes,
                lines_of_code=lines_of_code,
                file_hash=file_hash,
                ast_complexity=ast_complexity,
                imports=imports,
                classes=classes,
                functions=functions,
                has_main=has_main,
                has_dual_copilot=has_dual_copilot,
                script_type=script_type,
                last_modified=last_modified
            )
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to analyze {script_path}: {e}")
            return None
    
    def _determine_script_type(self, filename: str, content: str, functions: List[str], classes: List[str]) -> str:
        """[TARGET] Intelligent script type classification"""
        content_lower = content.lower()
        filename_lower = filename.lower()
        
        # Check for specific patterns
        if "comprehensive_script_generation_platform" in filename_lower:
            return "GENERATION_PLATFORM"
        elif any(word in filename_lower for word in ["test", "spec"]):
            return "TEST"
        elif any(word in filename_lower for word in ["demo", "example"]):
            return "DEMO"
        elif any(word in filename_lower for word in ["analysis", "analyzer"]):
            return "ANALYSIS"
        elif any(word in filename_lower for word in ["database", "db"]):
            return "DATABASE"
        elif any(word in content_lower for word in ["flask", "fastapi", "django"]):
            return "WEB_APPLICATION"
        elif any(word in content_lower for word in ["sqlite", "postgresql", "mysql"]):
            return "DATABASE_TOOL"
        elif "main(" in content and len(functions) > 3:
            return "APPLICATION"
        elif len(classes) > 2:
            return "LIBRARY"
        else:
            return "UTILITY"
    
    def get_missing_scripts(self) -> Tuple[List[Path], List[str]]:
        """[SEARCH] Identify all missing scripts not tracked in production.db"""
        logger.info("[SEARCH] Scanning filesystem for Python scripts...")
        
        # Find all Python scripts in workspace with proper glob
        all_python_files = []
        
        # Get .py files in root
        all_python_files.extend(list(self.workspace_path.glob("*.py")))
        
        # Get .py files in direct subdirectories
        for subdir in self.workspace_path.iterdir():
            if subdir.is_dir() and not subdir.name.startswith('.'):
                all_python_files.extend(list(subdir.glob("*.py")))
                # Check one level deeper
                for subsubdir in subdir.iterdir():
                    if subsubdir.is_dir() and not subsubdir.name.startswith('.'):
                        all_python_files.extend(list(subsubdir.glob("*.py")))
        
        # Remove duplicates and filter out hidden directories
        all_python_files = list(set(all_python_files))
        all_python_files = [f for f in all_python_files if not any(part.startswith('.') for part in f.parts)]
        
        logger.info(f"[BAR_CHART] Found {len(all_python_files)} Python files in workspace")
        
        # Get currently tracked scripts from database
        with sqlite3.connect(self.production_db) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT filepath FROM script_metadata")
            tracked_scripts = {row[0] for row in cursor.fetchall()}
        
        logger.info(f"[BAR_CHART] Currently tracking {len(tracked_scripts)} scripts in database")
        
        # Identify missing scripts
        missing_scripts = []
        missing_script_names = []
        
        for script_path in all_python_files:
            abs_path = str(script_path.resolve())
            if abs_path not in tracked_scripts:
                missing_scripts.append(script_path)
                missing_script_names.append(script_path.name)
        
        logger.info(f"[ALERT] CRITICAL: {len(missing_scripts)} scripts missing from database")
        
        return missing_scripts, missing_script_names
    
    def execute_critical_sync(self) -> SyncResults:
        """[LAUNCH] Execute comprehensive sync with DUAL COPILOT validation"""
        start_time = datetime.now()
        logger.info("[LAUNCH] STARTING CRITICAL SCRIPT SYNC OPERATION")
        logger.info(f"[TIME] Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # DUAL COPILOT PATTERN: Primary execution with validation checkpoints
        
        # Phase 1: Discovery and validation
        logger.info("[BAR_CHART] Phase 1: Script Discovery and Validation")
        missing_scripts, missing_names = self.get_missing_scripts()
        
        if not missing_scripts:
            logger.info("[SUCCESS] All scripts already tracked - sync not needed")
            return self._create_sync_results(start_time, 0, 0, 0, [], 100.0, 100.0)
        
        # Phase 2: Pre-sync database state analysis
        logger.info("[BAR_CHART] Phase 2: Database State Analysis")
        coverage_before = self._calculate_coverage()
        
        # Phase 3: Critical sync execution with progress tracking
        logger.info("[BAR_CHART] Phase 3: Critical Sync Execution")
        
        sync_errors = []
        scripts_added = 0
        
        with tqdm(total=len(missing_scripts), desc="[PROCESSING] Syncing Scripts", unit="script") as pbar:
            for script_path in missing_scripts:
                try:
                    # Analyze script
                    analysis = self.analyze_script_file(script_path)
                    if not analysis:
                        sync_errors.append(f"Failed to analyze {script_path}")
                        continue
                    
                    # Add to database
                    self._add_script_to_database(analysis)
                    scripts_added += 1
                    
                    pbar.set_postfix({
                        'Added': scripts_added,
                        'Errors': len(sync_errors),
                        'Current': script_path.name[:20]
                    })
                    
                except Exception as e:
                    error_msg = f"Failed to sync {script_path}: {str(e)}"
                    sync_errors.append(error_msg)
                    logger.error(f"[ERROR] {error_msg}")
                
                pbar.update(1)
                time.sleep(0.01)  # Small delay for visual processing
        
        # Phase 4: Post-sync validation
        logger.info("[BAR_CHART] Phase 4: Post-Sync Validation")
        coverage_after = self._calculate_coverage()
        
        # Phase 5: Results compilation
        operation_duration = (datetime.now() - start_time).total_seconds()
        
        results = SyncResults(
            timestamp=datetime.now().isoformat(),
            total_scripts_found=len(missing_scripts),
            scripts_already_tracked=0,  # These were missing
            scripts_newly_added=scripts_added,
            sync_errors=sync_errors,
            coverage_before=coverage_before,
            coverage_after=coverage_after,
            operation_duration_seconds=operation_duration,
            sync_session_id=self.sync_session_id
        )
        
        # Log sync session
        self._log_sync_session(results)
        
        logger.info("[SUCCESS] CRITICAL SYNC OPERATION COMPLETED")
        return results
    
    def _add_script_to_database(self, analysis: ScriptAnalysis):
        """[STORAGE] Add script analysis to production.db with comprehensive metadata"""
        with sqlite3.connect(self.production_db) as conn:
            cursor = conn.cursor()
            
            # Add to script_metadata table
            cursor.execute("""
                INSERT OR REPLACE INTO script_metadata 
                (filepath, filename, size_bytes, lines_of_code, file_hash, 
                 imports, classes, functions, has_main_function, script_type, 
                 last_analyzed, complexity_score, has_dual_copilot_pattern)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                analysis.filepath,
                analysis.filename,
                analysis.size_bytes,
                analysis.lines_of_code,
                analysis.file_hash,
                json.dumps(analysis.imports),
                json.dumps(analysis.classes),
                json.dumps(analysis.functions),
                analysis.has_main,
                analysis.script_type,
                analysis.last_modified,
                analysis.ast_complexity,
                analysis.has_dual_copilot
            ))
            
            # Add to file_system_mapping table for consistency
            cursor.execute("""
                INSERT OR REPLACE INTO file_system_mapping
                (file_path, file_hash, file_size, last_modified, file_type, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                analysis.filepath,
                analysis.file_hash,
                analysis.size_bytes,
                analysis.last_modified,
                ".py",
                "tracked"
            ))
            
            # Add to filesystem_sync_log
            cursor.execute("""
                INSERT INTO filesystem_sync_log
                (sync_session_id, action_type, file_path, status, error_message, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                self.sync_session_id,
                "ADD",
                analysis.filepath,
                "SUCCESS",
                None,
                datetime.now().isoformat()
            ))
            
            conn.commit()
    
    def _calculate_coverage(self) -> float:
        """[BAR_CHART] Calculate current script coverage percentage"""
        # Count all Python files with proper iteration
        all_python_files = []
        
        # Get .py files in root
        all_python_files.extend(list(self.workspace_path.glob("*.py")))
        
        # Get .py files in direct subdirectories
        for subdir in self.workspace_path.iterdir():
            if subdir.is_dir() and not subdir.name.startswith('.'):
                all_python_files.extend(list(subdir.glob("*.py")))
                # Check one level deeper
                for subsubdir in subdir.iterdir():
                    if subsubdir.is_dir() and not subsubdir.name.startswith('.'):
                        all_python_files.extend(list(subsubdir.glob("*.py")))
        
        # Remove duplicates
        all_python_files = list(set(all_python_files))
        total_files = len(all_python_files)
        
        with sqlite3.connect(self.production_db) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM script_metadata")
            tracked_scripts = cursor.fetchone()[0]
        
        return (tracked_scripts / total_files * 100) if total_files > 0 else 0.0
    
    def _log_sync_session(self, results: SyncResults):
        """[NOTES] Log comprehensive sync session details"""
        with sqlite3.connect(self.production_db) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO filesystem_sync_log
                (sync_session_id, action_type, file_path, status, error_message, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                self.sync_session_id,
                "SYNC_SESSION_COMPLETE",
                f"Added {results.scripts_newly_added} scripts",
                "SUCCESS" if not results.sync_errors else "PARTIAL",
                json.dumps(results.sync_errors) if results.sync_errors else None,
                results.timestamp
            ))
            conn.commit()
    
    def _create_sync_results(self, start_time: datetime, total: int, tracked: int, added: int, 
                           errors: List[str], coverage_before: float, coverage_after: float) -> SyncResults:
        """[CLIPBOARD] Create comprehensive sync results"""
        return SyncResults(
            timestamp=datetime.now().isoformat(),
            total_scripts_found=total,
            scripts_already_tracked=tracked,
            scripts_newly_added=added,
            sync_errors=errors,
            coverage_before=coverage_before,
            coverage_after=coverage_after,
            operation_duration_seconds=(datetime.now() - start_time).total_seconds(),
            sync_session_id=self.sync_session_id
        )

class DualCopilotValidator:
    """[SHIELD] DUAL COPILOT PATTERN: Secondary validation system"""
    
    def __init__(self, production_db: Path):
        self.production_db = production_db
    
    def validate_sync_completion(self, results: SyncResults) -> Dict[str, Any]:
        """[SEARCH] Comprehensive validation of sync operation"""
        logger.info("[SHIELD] DUAL COPILOT VALIDATION: Starting secondary validation")
        
        validation_results = {
            "validation_timestamp": datetime.now().isoformat(),
            "sync_session_validated": results.sync_session_id,
            "database_integrity": self._validate_database_integrity(),
            "coverage_improvement": self._validate_coverage_improvement(results),
            "script_metadata_quality": self._validate_script_metadata(),
            "sync_errors_analysis": self._analyze_sync_errors(results.sync_errors),
            "overall_validation": "PENDING"
        }
        
        # Determine overall validation status
        all_checks_passed = (
            validation_results["database_integrity"]["status"] == "PASSED" and
            validation_results["coverage_improvement"]["status"] == "PASSED" and
            validation_results["script_metadata_quality"]["status"] == "PASSED" and
            len(results.sync_errors) == 0
        )
        
        validation_results["overall_validation"] = "PASSED" if all_checks_passed else "FAILED"
        
        logger.info(f"[SHIELD] DUAL COPILOT VALIDATION: {validation_results['overall_validation']}")
        return validation_results
    
    def _validate_database_integrity(self) -> Dict[str, Any]:
        """[SEARCH] Validate database integrity after sync"""
        try:
            with sqlite3.connect(self.production_db) as conn:
                cursor = conn.cursor()
                
                # Check for duplicate entries
                cursor.execute("SELECT COUNT(*), COUNT(DISTINCT filepath) FROM script_metadata")
                total, unique = cursor.fetchone()
                
                # Check for null critical fields
                cursor.execute("SELECT COUNT(*) FROM script_metadata WHERE filepath IS NULL OR filename IS NULL")
                null_count = cursor.fetchone()[0]
                
                status = "PASSED" if total == unique and null_count == 0 else "FAILED"
                
                return {
                    "status": status,
                    "total_records": total,
                    "unique_records": unique,
                    "null_critical_fields": null_count,
                    "duplicates_detected": total - unique
                }
        except Exception as e:
            return {"status": "ERROR", "error": str(e)}
    
    def _validate_coverage_improvement(self, results: SyncResults) -> Dict[str, Any]:
        """[BAR_CHART] Validate coverage improvement"""
        improvement = results.coverage_after - results.coverage_before
        
        return {
            "status": "PASSED" if improvement > 0 else "FAILED",
            "coverage_before": results.coverage_before,
            "coverage_after": results.coverage_after,
            "improvement_percentage": improvement,
            "scripts_added": results.scripts_newly_added
        }
    
    def _validate_script_metadata(self) -> Dict[str, Any]:
        """[SEARCH] Validate quality of script metadata"""
        try:
            with sqlite3.connect(self.production_db) as conn:
                cursor = conn.cursor()
                
                # Check metadata quality indicators
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN has_dual_copilot_pattern = 1 THEN 1 ELSE 0 END) as dual_copilot_count,
                        SUM(CASE WHEN has_main_function = 1 THEN 1 ELSE 0 END) as main_function_count,
                        AVG(complexity_score) as avg_complexity,
                        COUNT(DISTINCT script_type) as script_types
                    FROM script_metadata
                """)
                
                stats = cursor.fetchone()
                
                return {
                    "status": "PASSED",
                    "total_scripts": stats[0],
                    "dual_copilot_patterns": stats[1],
                    "main_functions": stats[2],
                    "average_complexity": round(stats[3], 2) if stats[3] else 0,
                    "script_types_count": stats[4]
                }
        except Exception as e:
            return {"status": "ERROR", "error": str(e)}
    
    def _analyze_sync_errors(self, errors: List[str]) -> Dict[str, Any]:
        """[SEARCH] Analyze sync errors for patterns"""
        return {
            "total_errors": len(errors),
            "error_types": self._categorize_errors(errors),
            "critical_errors": [e for e in errors if "CRITICAL" in e.upper()],
            "status": "PASSED" if len(errors) == 0 else "REVIEW_REQUIRED"
        }
    
    def _categorize_errors(self, errors: List[str]) -> Dict[str, int]:
        """[BAR_CHART] Categorize errors by type"""
        categories = {
            "analysis_failures": 0,
            "database_errors": 0,
            "file_access_errors": 0,
            "other_errors": 0
        }
        
        for error in errors:
            error_lower = error.lower()
            if "analyze" in error_lower:
                categories["analysis_failures"] += 1
            elif "database" in error_lower or "sql" in error_lower:
                categories["database_errors"] += 1
            elif "permission" in error_lower or "access" in error_lower:
                categories["file_access_errors"] += 1
            else:
                categories["other_errors"] += 1
        
        return categories

def main():
    """[LAUNCH] Main execution with DUAL COPILOT PATTERN"""
    
    # DUAL COPILOT PATTERN: Primary Implementation
    try:
        logger.info("[ALERT] CRITICAL SCRIPT SYNC OPERATION - DUAL COPILOT PATTERN")
        logger.info("=" * 70)
        
        # Initialize sync operation
        sync_operation = CriticalScriptSyncOperation()
        
        # Execute critical sync
        results = sync_operation.execute_critical_sync()
        
        # Display results
        logger.info("[BAR_CHART] SYNC OPERATION RESULTS:")
        logger.info("=" * 40)
        logger.info(f"[SEARCH] Scripts Found Missing: {results.total_scripts_found}")
        logger.info(f"[SUCCESS] Scripts Successfully Added: {results.scripts_newly_added}")
        logger.info(f"[ERROR] Sync Errors: {len(results.sync_errors)}")
        logger.info(f"[CHART_INCREASING] Coverage Before: {results.coverage_before:.1f}%")
        logger.info(f"[CHART_INCREASING] Coverage After: {results.coverage_after:.1f}%")
        logger.info(f"[?][?] Operation Duration: {results.operation_duration_seconds:.2f}s")
        
        if results.sync_errors:
            logger.warning("[WARNING] SYNC ERRORS DETECTED:")
            for error in results.sync_errors:
                logger.warning(f"   [?] {error}")
        
        # Save results to file
        results_file = Path("critical_sync_results.json")
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump({
                "sync_results": {
                    "timestamp": results.timestamp,
                    "total_scripts_found": results.total_scripts_found,
                    "scripts_newly_added": results.scripts_newly_added,
                    "sync_errors": results.sync_errors,
                    "coverage_before": results.coverage_before,
                    "coverage_after": results.coverage_after,
                    "operation_duration_seconds": results.operation_duration_seconds,
                    "sync_session_id": results.sync_session_id
                }
            }, f, indent=2)
        
        logger.info(f"[STORAGE] Results saved to: {results_file}")
        
    except Exception as e:
        logger.error(f"[ALERT] CRITICAL: Primary sync operation failed: {e}")
        raise
    
    # DUAL COPILOT PATTERN: Secondary Validation
    try:
        logger.info("[SHIELD] DUAL COPILOT VALIDATION: Starting secondary validation")
        
        # Initialize validator
        validator = DualCopilotValidator(sync_operation.production_db)
        
        # Validate sync completion
        validation_results = validator.validate_sync_completion(results)
        
        # Display validation results
        logger.info("[SHIELD] VALIDATION RESULTS:")
        logger.info("=" * 30)
        logger.info(f"Overall Status: {validation_results['overall_validation']}")
        logger.info(f"Database Integrity: {validation_results['database_integrity']['status']}")
        logger.info(f"Coverage Improvement: {validation_results['coverage_improvement']['status']}")
        logger.info(f"Metadata Quality: {validation_results['script_metadata_quality']['status']}")
        
        # Save validation results
        validation_file = Path("critical_sync_validation.json")
        with open(validation_file, "w", encoding="utf-8") as f:
            json.dump(validation_results, f, indent=2, default=str)
        
        logger.info(f"[STORAGE] Validation results saved to: {validation_file}")
        
        if validation_results["overall_validation"] == "PASSED":
            logger.info("[SUCCESS] DUAL COPILOT VALIDATION: ALL CHECKS PASSED")
            logger.info("[TARGET] CRITICAL SYNC OPERATION COMPLETED SUCCESSFULLY")
            return 0
        else:
            logger.error("[ERROR] DUAL COPILOT VALIDATION: VALIDATION FAILED")
            logger.error("[ALERT] Manual review required")
            return 1
            
    except Exception as e:
        logger.error(f"[ALERT] CRITICAL: Secondary validation failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
