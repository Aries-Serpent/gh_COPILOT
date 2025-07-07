#!/usr/bin/env python3
"""
[ALERT] SIMPLIFIED CRITICAL SCRIPT SYNC - DUAL COPILOT PATTERN
=========================================================

MISSION: Immediate sync of missing scripts to production.db using existing schema
- Works with current database structure
- Complete coverage validation and reporting
- Zero-tolerance anti-recursion protocols enforced

Author: Critical Sync Operations Team
Version: 1.0.1 - Schema Compatible
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

# Configure enterprise logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('simplified_critical_sync.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class SyncResults:
    """Simplified sync operation results"""
    timestamp: str
    total_scripts_found: int
    scripts_newly_added: int
    sync_errors: List[str]
    coverage_before: float
    coverage_after: float
    operation_duration_seconds: float

class SimplifiedCriticalScriptSync:
    """[ALERT] SIMPLIFIED: Emergency script sync with existing schema"""
    
    def __init__(self):
        """Initialize sync operation"""
        self.workspace_path = Path("e:/gh_COPILOT")
        self.production_db = self.workspace_path / "databases" / "production.db"
        self.sync_session_id = f"SIMPLIFIED_SYNC_{int(datetime.now().timestamp())}"
        
        # Validate database accessibility
        if not self.production_db.exists():
            raise FileNotFoundError(f"[ALERT] CRITICAL: production.db not found at {self.production_db}")
        
        logger.info("[LAUNCH] SIMPLIFIED CRITICAL SYNC OPERATION INITIALIZED")
        logger.info(f"Session ID: {self.sync_session_id}")
    
    def analyze_script_file(self, script_path: Path) -> Optional[Dict[str, Any]]:
        """[SEARCH] Simple script analysis compatible with existing schema"""
        try:
            # Read file content
            with open(script_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            if not content.strip():
                logger.warning(f"[WARNING] Empty script file: {script_path}")
                return None
            
            # Basic file metrics
            size_bytes = script_path.stat().st_size
            lines_of_code = len([line for line in content.split('\n') if line.strip()])
            last_modified = datetime.fromtimestamp(script_path.stat().st_mtime).isoformat()
            
            # Simple AST analysis
            complexity_score = 0
            imports = []
            classes = []
            functions = []
            
            try:
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        functions.append(node.name)
                        complexity_score += 2
                    elif isinstance(node, ast.ClassDef):
                        classes.append(node.name)
                        complexity_score += 3
                    elif isinstance(node, (ast.If, ast.For, ast.While, ast.Try)):
                        complexity_score += 1
                    elif isinstance(node, (ast.Import, ast.ImportFrom)):
                        if isinstance(node, ast.Import):
                            imports.extend([alias.name for alias in node.names])
                        else:
                            imports.append(node.module or "relative_import")
                
            except SyntaxError:
                logger.warning(f"[WARNING] Syntax error in {script_path} - treating as basic script")
            
            # Determine category
            filename_lower = script_path.name.lower()
            if "comprehensive_script_generation_platform" in filename_lower:
                category = "GENERATION_PLATFORM"
            elif any(word in filename_lower for word in ["test", "demo"]):
                category = "DEMO"
            elif any(word in filename_lower for word in ["analysis", "analyzer"]):
                category = "ANALYSIS"
            elif any(word in filename_lower for word in ["database", "db"]):
                category = "DATABASE"
            else:
                category = "UTILITY"
            
            return {
                "filepath": str(script_path.resolve()),
                "filename": script_path.name,
                "size_bytes": size_bytes,
                "lines_of_code": lines_of_code,
                "functions": json.dumps(functions),
                "classes": json.dumps(classes),
                "imports": json.dumps(imports),
                "dependencies": json.dumps([]),
                "patterns": json.dumps([]),
                "database_connections": json.dumps([]),
                "complexity_score": complexity_score,
                "last_modified": last_modified,
                "category": category,
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to analyze {script_path}: {e}")
            return None
    
    def get_missing_scripts(self) -> List[Path]:
        """[SEARCH] Find missing scripts using safe file discovery"""
        logger.info("[SEARCH] Scanning for Python scripts...")
        
        # Find Python files safely
        all_python_files = []
        
        # Root directory .py files
        for file in self.workspace_path.glob("*.py"):
            all_python_files.append(file)
        
        # Subdirectory .py files (one level deep)
        for subdir in self.workspace_path.iterdir():
            if subdir.is_dir() and not subdir.name.startswith('.'):
                for file in subdir.glob("*.py"):
                    all_python_files.append(file)
                
                # Two levels deep for generated_scripts, etc.
                for subsubdir in subdir.iterdir():
                    if subsubdir.is_dir() and not subsubdir.name.startswith('.'):
                        for file in subsubdir.glob("*.py"):
                            all_python_files.append(file)
        
        logger.info(f"[BAR_CHART] Found {len(all_python_files)} Python files")
        
        # Get tracked scripts
        with sqlite3.connect(self.production_db) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT filepath FROM script_metadata")
            tracked_paths = {row[0] for row in cursor.fetchall()}
        
        # Find missing
        missing_scripts = []
        for script_path in all_python_files:
            if str(script_path.resolve()) not in tracked_paths:
                missing_scripts.append(script_path)
        
        logger.info(f"[ALERT] Missing: {len(missing_scripts)} scripts")
        return missing_scripts
    
    def execute_sync(self) -> SyncResults:
        """[LAUNCH] Execute simplified sync operation"""
        start_time = datetime.now()
        logger.info("[LAUNCH] STARTING SIMPLIFIED SYNC OPERATION")
        
        # Get missing scripts
        missing_scripts = self.get_missing_scripts()
        
        if not missing_scripts:
            logger.info("[SUCCESS] All scripts already tracked")
            return SyncResults(
                timestamp=datetime.now().isoformat(),
                total_scripts_found=0,
                scripts_newly_added=0,
                sync_errors=[],
                coverage_before=100.0,
                coverage_after=100.0,
                operation_duration_seconds=0.0
            )
        
        # Calculate initial coverage
        coverage_before = self._calculate_coverage()
        
        # Sync scripts
        sync_errors = []
        scripts_added = 0
        
        logger.info(f"[PROCESSING] Syncing {len(missing_scripts)} missing scripts...")
        
        with tqdm(total=len(missing_scripts), desc="[PROCESSING] Syncing", unit="script") as pbar:
            for script_path in missing_scripts:
                try:
                    # Analyze script
                    analysis = self.analyze_script_file(script_path)
                    if not analysis:
                        sync_errors.append(f"Failed to analyze {script_path.name}")
                        continue
                    
                    # Add to database using existing schema
                    with sqlite3.connect(self.production_db) as conn:
                        cursor = conn.cursor()
                        cursor.execute("""
                            INSERT OR REPLACE INTO script_metadata 
                            (filepath, filename, size_bytes, lines_of_code, functions, 
                             classes, imports, dependencies, patterns, database_connections,
                             complexity_score, last_modified, category, analysis_timestamp)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            analysis["filepath"],
                            analysis["filename"],
                            analysis["size_bytes"],
                            analysis["lines_of_code"],
                            analysis["functions"],
                            analysis["classes"],
                            analysis["imports"],
                            analysis["dependencies"],
                            analysis["patterns"],
                            analysis["database_connections"],
                            analysis["complexity_score"],
                            analysis["last_modified"],
                            analysis["category"],
                            analysis["analysis_timestamp"]
                        ))
                        
                        # Log sync action
                        cursor.execute("""
                            INSERT INTO filesystem_sync_log
                            (sync_session_id, action_type, file_path, status, error_message, sync_timestamp)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (
                            self.sync_session_id,
                            "ADD",
                            analysis["filepath"],
                            "SUCCESS",
                            None,
                            datetime.now().isoformat()
                        ))
                        
                        conn.commit()
                    
                    scripts_added += 1
                    
                    pbar.set_postfix({
                        'Added': scripts_added,
                        'Current': script_path.name[:20]
                    })
                    
                except Exception as e:
                    error_msg = f"Failed to sync {script_path.name}: {str(e)}"
                    sync_errors.append(error_msg)
                    logger.error(f"[ERROR] {error_msg}")
                
                pbar.update(1)
                time.sleep(0.01)
        
        # Calculate final coverage
        coverage_after = self._calculate_coverage()
        operation_duration = (datetime.now() - start_time).total_seconds()
        
        results = SyncResults(
            timestamp=datetime.now().isoformat(),
            total_scripts_found=len(missing_scripts),
            scripts_newly_added=scripts_added,
            sync_errors=sync_errors,
            coverage_before=coverage_before,
            coverage_after=coverage_after,
            operation_duration_seconds=operation_duration
        )
        
        # Log session completion
        with sqlite3.connect(self.production_db) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO filesystem_sync_log
                (sync_session_id, action_type, file_path, status, error_message, sync_timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                self.sync_session_id,
                "SYNC_COMPLETE",
                f"Added {scripts_added} scripts",
                "SUCCESS" if not sync_errors else "PARTIAL",
                json.dumps(sync_errors) if sync_errors else None,
                datetime.now().isoformat()
            ))
            conn.commit()
        
        logger.info("[SUCCESS] SIMPLIFIED SYNC OPERATION COMPLETED")
        return results
    
    def _calculate_coverage(self) -> float:
        """[BAR_CHART] Calculate coverage percentage"""
        # Count all Python files
        all_files = []
        for file in self.workspace_path.glob("*.py"):
            all_files.append(file)
        for subdir in self.workspace_path.iterdir():
            if subdir.is_dir() and not subdir.name.startswith('.'):
                for file in subdir.glob("*.py"):
                    all_files.append(file)
                for subsubdir in subdir.iterdir():
                    if subsubdir.is_dir() and not subsubdir.name.startswith('.'):
                        for file in subsubdir.glob("*.py"):
                            all_files.append(file)
        
        total_files = len(set(all_files))
        
        # Count tracked files
        with sqlite3.connect(self.production_db) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM script_metadata")
            tracked_files = cursor.fetchone()[0]
        
        return (tracked_files / total_files * 100) if total_files > 0 else 0.0

def main():
    """[LAUNCH] Main execution with DUAL COPILOT PATTERN"""
    
    try:
        logger.info("[ALERT] SIMPLIFIED CRITICAL SCRIPT SYNC - DUAL COPILOT PATTERN")
        logger.info("=" * 70)
        
        # Initialize and execute sync
        sync_operation = SimplifiedCriticalScriptSync()
        results = sync_operation.execute_sync()
        
        # Display comprehensive results
        logger.info("[BAR_CHART] SYNC OPERATION RESULTS:")
        logger.info("=" * 40)
        logger.info(f"[SEARCH] Scripts Found Missing: {results.total_scripts_found}")
        logger.info(f"[SUCCESS] Scripts Successfully Added: {results.scripts_newly_added}")
        logger.info(f"[ERROR] Sync Errors: {len(results.sync_errors)}")
        logger.info(f"[CHART_INCREASING] Coverage Before: {results.coverage_before:.1f}%")
        logger.info(f"[CHART_INCREASING] Coverage After: {results.coverage_after:.1f}%")
        logger.info(f"[CHART_INCREASING] Coverage Improvement: {results.coverage_after - results.coverage_before:.1f}%")
        logger.info(f"[?][?] Operation Duration: {results.operation_duration_seconds:.2f}s")
        
        if results.sync_errors:
            logger.warning("[WARNING] SYNC ERRORS:")
            for error in results.sync_errors:
                logger.warning(f"   [?] {error}")
        
        # Save results
        results_file = Path("simplified_sync_results.json")
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump({
                "sync_results": {
                    "timestamp": results.timestamp,
                    "total_scripts_found": results.total_scripts_found,
                    "scripts_newly_added": results.scripts_newly_added,
                    "sync_errors": results.sync_errors,
                    "coverage_before": results.coverage_before,
                    "coverage_after": results.coverage_after,
                    "coverage_improvement": results.coverage_after - results.coverage_before,
                    "operation_duration_seconds": results.operation_duration_seconds
                }
            }, f, indent=2)
        
        logger.info(f"[STORAGE] Results saved to: {results_file}")
        
        # Final coverage validation
        if results.coverage_after > 95.0:
            logger.info("[TARGET] EXCELLENT: Script coverage exceeds 95%")
            return 0
        elif results.coverage_after > 90.0:
            logger.info("[SUCCESS] GOOD: Script coverage exceeds 90%")
            return 0
        else:
            logger.warning(f"[WARNING] Coverage at {results.coverage_after:.1f}% - may need further review")
            return 0
        
    except Exception as e:
        logger.error(f"[ALERT] CRITICAL: Sync operation failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
