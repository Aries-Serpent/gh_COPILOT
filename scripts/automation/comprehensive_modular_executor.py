#!/usr/bin/env python3
"""
Comprehensive Modular Script Organization Executor
DUAL COPILOT PATTERN - Enterprise Modular Organization Implementation
"""

import os
import sys
import sqlite3
import json
import hashlib
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
from tqdm import tqdm

# MANDATORY: Visual processing indicators
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ComprehensiveModularExecutor:
    """🚀 Execute Complete Modular Script Organization Plan"""
    
    def __init__(self, workspace_root: str = "e:/gh_COPILOT"):
        self.workspace_root = Path(workspace_root)
        self.start_time = datetime.now()
        
        # CRITICAL: Anti-recursion validation
        self._validate_environment_compliance()
        
        # Directory structure
        self.scripts_dir = self.workspace_root / "scripts"
        self.utils_dir = self.workspace_root / "utils"
        self.archives_dir = self.workspace_root / "archives"
        self.databases_dir = self.workspace_root / "databases"
        
        logger.info("="*80)
        logger.info("🚀 COMPREHENSIVE MODULAR EXECUTOR INITIALIZED")
        logger.info(f"Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Workspace: {self.workspace_root}")
        logger.info("="*80)
    
    def _validate_environment_compliance(self):
        """CRITICAL: Validate workspace integrity"""
        if not str(self.workspace_root).endswith("gh_COPILOT"):
            raise RuntimeError("CRITICAL: Invalid workspace root")
        
        # Check for recursive violations
        forbidden_patterns = ["backup", "temp", "copy"]
        for pattern in forbidden_patterns:
            if pattern in str(self.workspace_root).lower():
                raise RuntimeError(f"CRITICAL: Forbidden pattern {pattern} in workspace")
        
        logger.info("✅ Environment compliance validated")
    
    def execute_complete_modular_organization(self) -> Dict[str, Any]:
        """Execute all phases of modular organization"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "phases_completed": [],
            "total_scripts": 0,
            "organized_scripts": 0,
            "database_coverage": 0.0,
            "status": "IN_PROGRESS"
        }
        
        try:
            # Phase 1: Database Validation
            phase1_results = self.execute_phase1_database_validation()
            results["phases_completed"].append("Database Validation")
            results["total_scripts"] = phase1_results["repository_scripts"]
            results["database_coverage"] = phase1_results.get("coverage", 0.0)
            
            # Phase 2: Create Script Organization Structure
            phase2_results = self.execute_phase2_create_structure()
            results["phases_completed"].append("Structure Creation")
            
            # Phase 3: Organize Scripts by Category
            phase3_results = self.execute_phase3_organize_scripts()
            results["phases_completed"].append("Script Organization")
            results["organized_scripts"] = phase3_results["organized_count"]
            
            # Phase 4: Create Utility Modules
            phase4_results = self.execute_phase4_create_utilities()
            results["phases_completed"].append("Utility Modules")
            
            # Phase 5: Clean Root Directory
            phase5_results = self.execute_phase5_clean_root()
            results["phases_completed"].append("Root Cleanup")
            
            # Phase 6: Update Database Mappings
            phase6_results = self.execute_phase6_update_database()
            results["phases_completed"].append("Database Updates")
            
            results["status"] = "COMPLETED"
            
        except Exception as e:
            logger.error(f"❌ Execution failed: {e}")
            results["status"] = "FAILED"
            results["error"] = str(e)
        
        return results
    
    def execute_phase1_database_validation(self) -> Dict[str, Any]:
        """Phase 1: Validate all scripts are properly stored in databases"""
        logger.info("🔍 PHASE 1: DATABASE SCRIPT VALIDATION")
        logger.info("="*60)
        
        # Scan repository scripts
        repository_scripts = {}
        script_extensions = {'.py', '.ps1', '.sh', '.bat'}
        
        logger.info("📁 Scanning repository for scripts...")
        script_count = 0
        
        for script_path in self.workspace_root.rglob("*"):
            if (script_path.is_file() and 
                script_path.suffix in script_extensions and
                not any(part.startswith('.') for part in script_path.parts) and
                'archives' not in script_path.parts and
                '__pycache__' not in str(script_path)):
                
                relative_path = script_path.relative_to(self.workspace_root)
                
                try:
                    with open(script_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    repository_scripts[str(relative_path)] = {
                        'absolute_path': str(script_path),
                        'content': content,
                        'hash': hashlib.sha256(content.encode()).hexdigest(),
                        'size': script_path.stat().st_size,
                        'extension': script_path.suffix
                    }
                    script_count += 1
                    
                except Exception as e:
                    logger.warning(f"⚠️ Error reading {script_path}: {e}")
        
        logger.info(f"📊 Repository Scripts Found: {script_count}")
        
        # Check database storage
        db_count = 0
        coverage = 0.0
        
        if self.databases_dir.exists():
            production_db = self.databases_dir / "production.db"
            if production_db.exists():
                try:
                    with sqlite3.connect(production_db) as conn:
                        cursor = conn.cursor()
                        cursor.execute("SELECT COUNT(*) FROM enhanced_script_tracking")
                        db_count = cursor.fetchone()[0]
                        logger.info(f"📊 Database Scripts: {db_count}")
                        
                        coverage = (db_count / script_count * 100) if script_count > 0 else 0
                        logger.info(f"📈 Database Coverage: {coverage:.1f}%")
                        
                except Exception as e:
                    logger.warning(f"⚠️ Database check failed: {e}")
        
        return {
            "repository_scripts": script_count,
            "database_scripts": db_count,
            "coverage": coverage,
            "status": "validated"
        }
    
    def execute_phase2_create_structure(self) -> Dict[str, Any]:
        """Phase 2: Create organized script directory structure"""
        logger.info("🏗️ PHASE 2: CREATING SCRIPT ORGANIZATION STRUCTURE")
        logger.info("="*60)
        
        # Create main directories
        directories_to_create = [
            self.scripts_dir,
            self.scripts_dir / "analysis",
            self.scripts_dir / "automation", 
            self.scripts_dir / "database",
            self.scripts_dir / "optimization",
            self.scripts_dir / "validation",
            self.scripts_dir / "enterprise",
            self.scripts_dir / "monitoring",
            self.scripts_dir / "utilities",
            self.utils_dir,
            self.archives_dir
        ]
        
        created_dirs = []
        for directory in directories_to_create:
            try:
                directory.mkdir(parents=True, exist_ok=True)
                created_dirs.append(str(directory))
                logger.info(f"✅ Created: {directory}")
            except Exception as e:
                logger.error(f"❌ Failed to create {directory}: {e}")
        
        return {"created_directories": len(created_dirs), "status": "completed"}
    
    def execute_phase3_organize_scripts(self) -> Dict[str, Any]:
        """Phase 3: Organize scripts into appropriate categories"""
        logger.info("📂 PHASE 3: ORGANIZING SCRIPTS BY CATEGORY")
        logger.info("="*60)
        
        # Define categorization patterns
        categorization_patterns = {
            "analysis": ["analysis", "report", "breakdown", "assess", "evaluate"],
            "automation": ["auto", "orchestr", "executor", "launcher", "processor"],
            "database": ["database", "db", "sql", "table", "query", "backup"],
            "optimization": ["optim", "enhance", "improve", "boost", "accelerate"],
            "validation": ["valid", "test", "check", "verify", "compliance"],
            "enterprise": ["enterprise", "production", "deploy", "framework"],
            "monitoring": ["monitor", "log", "track", "watch", "alert"],
            "utilities": ["util", "helper", "tool", "common", "shared"]
        }
        
        organized_count = 0
        organization_log = []
        
        # Get all Python scripts in root
        root_scripts = list(self.workspace_root.glob("*.py"))
        
        logger.info(f"📊 Processing {len(root_scripts)} root scripts...")
        
        with tqdm(total=len(root_scripts), desc="📂 Organizing Scripts", unit="script") as pbar:
            for script_path in root_scripts:
                try:
                    # Determine category based on filename and content
                    category = self._determine_script_category(script_path, categorization_patterns)
                    
                    # Move script to appropriate category
                    target_dir = self.scripts_dir / category
                    target_path = target_dir / script_path.name
                    
                    # Avoid moving if already in correct location
                    if not target_path.exists():
                        shutil.move(str(script_path), str(target_path))
                        organized_count += 1
                        organization_log.append({
                            "script": script_path.name,
                            "category": category,
                            "target": str(target_path)
                        })
                        logger.info(f"📂 Moved {script_path.name} → {category}/")
                    
                    pbar.update(1)
                    
                except Exception as e:
                    logger.error(f"❌ Error organizing {script_path}: {e}")
                    pbar.update(1)
        
        return {
            "organized_count": organized_count,
            "organization_log": organization_log,
            "status": "completed"
        }
    
    def _determine_script_category(self, script_path: Path, patterns: Dict[str, List[str]]) -> str:
        """Determine the appropriate category for a script"""
        script_name = script_path.name.lower()
        
        # Check filename patterns
        for category, keywords in patterns.items():
            if any(keyword in script_name for keyword in keywords):
                return category
        
        # Default to utilities if no pattern matches
        return "utilities"
    
    def execute_phase4_create_utilities(self) -> Dict[str, Any]:
        """Phase 4: Create utility modules for shared functionality"""
        logger.info("🔧 PHASE 4: CREATING UTILITY MODULES")
        logger.info("="*60)
        
        utility_modules = {
            "configuration_utils.py": self._generate_configuration_utils(),
            "file_utils.py": self._generate_file_utils(),
            "database_utils.py": self._generate_database_utils(),
            "logging_utils.py": self._generate_logging_utils(),
            "validation_utils.py": self._generate_validation_utils()
        }
        
        created_modules = []
        for module_name, content in utility_modules.items():
            try:
                module_path = self.utils_dir / module_name
                with open(module_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                created_modules.append(module_name)
                logger.info(f"✅ Created: {module_name}")
            except Exception as e:
                logger.error(f"❌ Failed to create {module_name}: {e}")
        
        # Create __init__.py
        init_content = """# Utility modules for gh_COPILOT Enterprise Toolkit
__version__ = "1.0.0"
"""
        with open(self.utils_dir / "__init__.py", 'w', encoding='utf-8') as f:
            f.write(init_content)
        
        return {"created_modules": created_modules, "status": "completed"}
    
    def execute_phase5_clean_root(self) -> Dict[str, Any]:
        """Phase 5: Clean root directory to contain only critical files"""
        logger.info("🧹 PHASE 5: CLEANING ROOT DIRECTORY")
        logger.info("="*60)
        
        # Define critical files that should remain in root
        critical_files = {
            "README.md",
            "COPILOT_NAVIGATION_MAP.json",
            "requirements.txt", 
            "main.py",
            "package.json",
            "pyproject.toml",
            "Makefile",
            "CHANGELOG.md",
            "Dockerfile",
            "docker-compose.yml",
            ".env.example",
            ".flake8",
            ".gitignore"
        }
        
        moved_files = []
        root_files = list(self.workspace_root.glob("*"))
        
        for file_path in root_files:
            if (file_path.is_file() and 
                file_path.name not in critical_files and
                not file_path.name.startswith('.')):
                
                try:
                    # Determine appropriate destination
                    if file_path.suffix == '.py':
                        # Should have been moved in Phase 3
                        continue
                    elif file_path.suffix in ['.json', '.yml', '.yaml', '.toml']:
                        target_dir = self.workspace_root / "config"
                        target_dir.mkdir(exist_ok=True)
                    elif file_path.suffix in ['.md', '.txt', '.rst']:
                        target_dir = self.workspace_root / "documentation"
                        target_dir.mkdir(exist_ok=True)
                    else:
                        target_dir = self.workspace_root / "misc"
                        target_dir.mkdir(exist_ok=True)
                    
                    target_path = target_dir / file_path.name
                    if not target_path.exists():
                        shutil.move(str(file_path), str(target_path))
                        moved_files.append(file_path.name)
                        logger.info(f"📁 Moved {file_path.name} → {target_dir.name}/")
                    
                except Exception as e:
                    logger.error(f"❌ Error moving {file_path}: {e}")
        
        return {"moved_files": moved_files, "status": "completed"}
    
    def execute_phase6_update_database(self) -> Dict[str, Any]:
        """Phase 6: Update database mappings for new organization"""
        logger.info("🗄️ PHASE 6: UPDATING DATABASE MAPPINGS")
        logger.info("="*60)
        
        updated_mappings = 0
        
        if self.databases_dir.exists():
            production_db = self.databases_dir / "production.db"
            if production_db.exists():
                try:
                    with sqlite3.connect(production_db) as conn:
                        cursor = conn.cursor()
                        
                        # Create organization tracking table
                        cursor.execute("""
                            CREATE TABLE IF NOT EXISTS script_organization (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                script_name TEXT UNIQUE,
                                original_path TEXT,
                                new_path TEXT,
                                category TEXT,
                                organization_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                            )
                        """)
                        
                        # Update script paths in existing tables
                        for category_dir in self.scripts_dir.iterdir():
                            if category_dir.is_dir():
                                for script_file in category_dir.glob("*.py"):
                                    relative_path = script_file.relative_to(self.workspace_root)
                                    
                                    cursor.execute("""
                                        INSERT OR REPLACE INTO script_organization
                                        (script_name, original_path, new_path, category)
                                        VALUES (?, ?, ?, ?)
                                    """, (
                                        script_file.name,
                                        script_file.name,  # Was in root
                                        str(relative_path),
                                        category_dir.name
                                    ))
                                    updated_mappings += 1
                        
                        conn.commit()
                        logger.info(f"✅ Updated {updated_mappings} script mappings")
                        
                except Exception as e:
                    logger.error(f"❌ Database update failed: {e}")
        
        return {"updated_mappings": updated_mappings, "status": "completed"}
    
    def _generate_configuration_utils(self) -> str:
        """Generate configuration utilities module"""
        return '''"""Configuration utilities for gh_COPILOT Enterprise Toolkit"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional

def load_enterprise_configuration(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Load enterprise configuration with defaults"""
    if config_path is None:
        config_path = os.getenv("GH_COPILOT_WORKSPACE", "e:/gh_COPILOT") + "/config/enterprise.json"
    
    defaults = {
        "workspace_root": os.getenv("GH_COPILOT_WORKSPACE", "e:/gh_COPILOT"),
        "database_path": "databases/production.db",
        "logging_level": "INFO",
        "enterprise_mode": True
    }
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        defaults.update(config)
    except FileNotFoundError:
        pass  # Use defaults
    
    return defaults

def validate_environment_compliance() -> bool:
    """Validate enterprise environment compliance"""
    workspace = os.getenv("GH_COPILOT_WORKSPACE", "e:/gh_COPILOT")
    return workspace.endswith("gh_COPILOT")
'''
    
    def _generate_file_utils(self) -> str:
        """Generate file utilities module"""
        return '''"""File utilities for gh_COPILOT Enterprise Toolkit"""

import os
import shutil
from pathlib import Path
from typing import Optional, Union

def read_file_safely(file_path: Union[str, Path], encoding: str = 'utf-8') -> Optional[str]:
    """Read file with safe encoding handling"""
    try:
        with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
            return f.read()
    except Exception:
        return None

def write_file_safely(file_path: Union[str, Path], content: str, encoding: str = 'utf-8') -> bool:
    """Write file with safe error handling"""
    try:
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding=encoding) as f:
            f.write(content)
        return True
    except Exception:
        return False

def copy_file_safely(src: Union[str, Path], dst: Union[str, Path]) -> bool:
    """Copy file with safe error handling"""
    try:
        Path(dst).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        return True
    except Exception:
        return False
'''
    
    def _generate_database_utils(self) -> str:
        """Generate database utilities module"""
        return '''"""Database utilities for gh_COPILOT Enterprise Toolkit"""

import sqlite3
import os
from pathlib import Path
from contextlib import contextmanager
from typing import Optional, Iterator

@contextmanager
def get_enterprise_database_connection(db_name: str = "production.db") -> Iterator[sqlite3.Connection]:
    """Get enterprise database connection with proper handling"""
    workspace = os.getenv("GH_COPILOT_WORKSPACE", "e:/gh_COPILOT")
    db_path = Path(workspace) / "databases" / db_name
    
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        yield conn
    finally:
        if conn:
            conn.close()

def execute_safe_query(query: str, params: tuple = (), db_name: str = "production.db") -> Optional[list]:
    """Execute database query safely"""
    try:
        with get_enterprise_database_connection(db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
    except Exception:
        return None

def check_table_exists(table_name: str, db_name: str = "production.db") -> bool:
    """Check if table exists in database"""
    query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
    result = execute_safe_query(query, (table_name,), db_name)
    return bool(result)
'''
    
    def _generate_logging_utils(self) -> str:
        """Generate logging utilities module"""
        return '''"""Logging utilities for gh_COPILOT Enterprise Toolkit"""

import logging
import os
from pathlib import Path
from datetime import datetime

def setup_enterprise_logging(level: str = "INFO", log_file: str = None) -> logging.Logger:
    """Setup enterprise-grade logging configuration"""
    
    if log_file is None:
        workspace = os.getenv("GH_COPILOT_WORKSPACE", "e:/gh_COPILOT")
        log_dir = Path(workspace) / "logs"
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / f"enterprise_{datetime.now().strftime('%Y%m%d')}.log"
    
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger("gh_COPILOT")

def log_enterprise_operation(operation: str, status: str, details: str = "") -> None:
    """Log enterprise operation with standard format"""
    logger = logging.getLogger("gh_COPILOT")
    
    if status.upper() == "SUCCESS":
        logger.info(f"✅ {operation}: {details}")
    elif status.upper() == "WARNING":
        logger.warning(f"⚠️ {operation}: {details}")
    elif status.upper() == "ERROR":
        logger.error(f"❌ {operation}: {details}")
    else:
        logger.info(f"📊 {operation}: {details}")
'''
    
    def _generate_validation_utils(self) -> str:
        """Generate validation utilities module"""
        return '''"""Validation utilities for gh_COPILOT Enterprise Toolkit"""

import os
from pathlib import Path
from typing import List, Dict, Any

def validate_workspace_integrity() -> Dict[str, Any]:
    """Validate workspace integrity and structure"""
    workspace = Path(os.getenv("GH_COPILOT_WORKSPACE", "e:/gh_COPILOT"))
    
    validation_results = {
        "workspace_exists": workspace.exists(),
        "required_directories": {},
        "forbidden_patterns": [],
        "overall_status": "UNKNOWN"
    }
    
    # Check required directories
    required_dirs = ["databases", "scripts", "utils", "documentation"]
    for dir_name in required_dirs:
        dir_path = workspace / dir_name
        validation_results["required_directories"][dir_name] = dir_path.exists()
    
    # Check for forbidden patterns (anti-recursion)
    forbidden = ["backup", "temp", "copy"]
    for pattern in forbidden:
        if pattern in str(workspace).lower():
            validation_results["forbidden_patterns"].append(pattern)
    
    # Determine overall status
    if (validation_results["workspace_exists"] and 
        all(validation_results["required_directories"].values()) and
        not validation_results["forbidden_patterns"]):
        validation_results["overall_status"] = "VALID"
    else:
        validation_results["overall_status"] = "INVALID"
    
    return validation_results

def validate_script_organization() -> Dict[str, Any]:
    """Validate script organization structure"""
    workspace = Path(os.getenv("GH_COPILOT_WORKSPACE", "e:/gh_COPILOT"))
    scripts_dir = workspace / "scripts"
    
    organization_status = {
        "scripts_directory_exists": scripts_dir.exists(),
        "categories": {},
        "root_python_files": 0,
        "organized_python_files": 0,
        "organization_percentage": 0.0
    }
    
    if scripts_dir.exists():
        # Count organized scripts
        for category_dir in scripts_dir.iterdir():
            if category_dir.is_dir():
                py_files = list(category_dir.glob("*.py"))
                organization_status["categories"][category_dir.name] = len(py_files)
                organization_status["organized_python_files"] += len(py_files)
    
    # Count root Python files
    root_py_files = list(workspace.glob("*.py"))
    organization_status["root_python_files"] = len(root_py_files)
    
    # Calculate organization percentage
    total_scripts = organization_status["organized_python_files"] + organization_status["root_python_files"]
    if total_scripts > 0:
        organization_status["organization_percentage"] = (
            organization_status["organized_python_files"] / total_scripts * 100
        )
    
    return organization_status
'''


def main():
    """Execute comprehensive modular organization"""
    try:
        executor = ComprehensiveModularExecutor()
        results = executor.execute_complete_modular_organization()
        
        # Log final results
        logger.info("="*80)
        logger.info("🏆 COMPREHENSIVE MODULAR ORGANIZATION COMPLETE")
        logger.info("="*80)
        logger.info(f"Status: {results['status']}")
        logger.info(f"Phases Completed: {len(results['phases_completed'])}")
        logger.info(f"Total Scripts: {results['total_scripts']}")
        logger.info(f"Organized Scripts: {results['organized_scripts']}")
        logger.info(f"Database Coverage: {results['database_coverage']:.1f}%")
        
        for phase in results['phases_completed']:
            logger.info(f"✅ {phase}")
        
        duration = (datetime.now() - executor.start_time).total_seconds()
        logger.info(f"Total Duration: {duration:.1f} seconds")
        logger.info("="*80)
        
        return results
        
    except Exception as e:
        logger.error(f"❌ Execution failed: {e}")
        raise

if __name__ == "__main__":
    main()
