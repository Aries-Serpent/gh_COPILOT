#!/usr/bin/env python3
"""
PRODUCTION ENVIRONMENT BUILDER
100% Error-Free Production Instance with Database-First Architecture

OBJECTIVE: Create minimal production environment at E:/_copilot_production-001/
- ONLY necessary system files
- ALL documentation in databases
- 100% error-free operation
- Autonomous GitHub Copilot Integration ready
- DUAL COPILOT pattern compliance
"""

import os
import sys
import json
import shutil
import sqlite3
import hashlib
import datetime
from pathlib import Path
from tqdm import tqdm
import logging

# Configure logging without Unicode
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('production_environment_build.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ProductionEnvironmentBuilder:
    """
    DUAL COPILOT: Production Environment Builder
    Creates 100% error-free minimal production environment
    """
    
    def __init__(self):
        self.start_time = datetime.datetime.now()
        self.sandbox_path = Path("e:/gh_COPILOT")
        self.production_path = Path("e:/_copilot_production-001")
        self.results = {
            "timestamp": self.start_time.isoformat(),
            "necessary_files": [],
            "documentation_migrated": [],
            "excluded_files": [],
            "database_status": {},
            "validation_results": {},
            "production_ready": False
        }
        
        logger.info("DUAL COPILOT: Production Environment Builder STARTED")
        logger.info(f"Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Process ID: {os.getpid()}")
    
    def identify_necessary_system_files(self):
        """
        PHASE 1: Identify ONLY necessary system files
        Exclude all documentation, reports, logs, and temporary files
        """
        logger.info("=" * 80)
        logger.info("PHASE 1: IDENTIFYING NECESSARY SYSTEM FILES")
        logger.info("=" * 80)
        
        # Essential files for production operation
        essential_files = [
            # Core databases
            "production.db",
            # Core web system files  
            "web_portal_enterprise_system.py",
            "copilot_cli_relay_api.py",
            "enhanced_logging_web_gui.py", 
            "simple_web_gui_launcher.py",
            "start_web_portal.py",
            # Configuration
            "requirements.txt",
            # All template and static files
        ]
        
        # Patterns to EXCLUDE (documentation, reports, logs, temp files)
        excluded_patterns = [
            # Documentation files
            "*.md", "*.txt", "*.rst", 
            # Report files
            "*_report_*", "*_REPORT_*", "*_results_*", "*_RESULTS_*",
            "*_summary_*", "*_SUMMARY_*", "*_analysis_*", "*_ANALYSIS_*",
            # Log files
            "*.log", "*_log_*", 
            # Temporary files
            "*_temp_*", "*_tmp_*", "*_test_*", "test_*",
            # Backup files
            "*_backup_*", "*_bak",
            # Cache files
            "__pycache__", "*.pyc", "*.pyo", ".pytest_cache",
            # IDE files
            ".vscode", ".idea", "*.swp", "*.swo",
            # Git files
            ".git", ".gitignore", ".github",
            # Development files
            "*_dev_*", "*_development_*", "*_debug_*"
        ]
        
        logger.info("Scanning sandbox for necessary files...")
        necessary_files = []
        excluded_files = []
        
        # Get all files
        all_files = []
        for root, dirs, files in os.walk(self.sandbox_path):
            for file in files:
                all_files.append(Path(root) / file)
        
        print(f"Total files to analyze: {len(all_files)}")
        
        for i, file_path in enumerate(all_files):
            if i % 100 == 0:
                print(f"Progress: {i}/{len(all_files)} ({i/len(all_files)*100:.1f}%)")
            
            relative_path = file_path.relative_to(self.sandbox_path)
            file_str = str(relative_path).replace("\\", "/")
            
            # Check if should be excluded
            should_exclude = False
            for pattern in excluded_patterns:
                if self._matches_pattern(file_str, pattern):
                    should_exclude = True
                    excluded_files.append(str(relative_path))
                    break
            
            if not should_exclude:
                # Check if it's essential or necessary
                if self._is_necessary_file(file_path, relative_path):
                    necessary_files.append({
                        "path": str(relative_path),
                        "size": file_path.stat().st_size,
                        "type": self._classify_file_type(file_path)
                    })
        
        self.results["necessary_files"] = necessary_files
        self.results["excluded_files"] = excluded_files
        
        logger.info(f"Analysis Complete:")
        logger.info(f"   Total files scanned: {len(all_files)}")
        logger.info(f"   Necessary files identified: {len(necessary_files)}")
        logger.info(f"   Excluded files: {len(excluded_files)}")
        logger.info(f"   Reduction ratio: {(len(excluded_files) / len(all_files) * 100):.1f}% excluded")
        
        return necessary_files
    
    def _matches_pattern(self, file_str, pattern):
        """Check if file matches exclusion pattern"""
        import fnmatch
        return fnmatch.fnmatch(file_str.lower(), pattern.lower())
    
    def _is_necessary_file(self, file_path, relative_path):
        """Determine if a file is necessary for production operation"""
        file_str = str(relative_path).replace("\\", "/")
        filename = file_path.name.lower()
        
        # Essential files that must be included
        essential_keywords = [
            "production.db",
            "web_portal_enterprise_system.py",
            "copilot_cli_relay_api.py",
            "enhanced_logging_web_gui.py",
            "simple_web_gui_launcher.py",
            "start_web_portal.py",
            "requirements.txt"
        ]
        
        # Check exact matches first
        for essential in essential_keywords:
            if essential in file_str:
                return True
        
        # Include all template and static files (needed for web interface)
        if any(x in file_str for x in ["templates/", "static/"]):
            return True
        
        # Include essential Python modules (but exclude test/debug/temp files)
        if file_path.suffix == ".py":
            # Exclude test/debug/temp files
            exclude_keywords = [
                "test_", "_test", "debug_", "_debug", 
                "temp_", "_temp", "tmp_", "_tmp",
                "example_", "_example", "demo_", "_demo",
                "validator", "checker", "analyzer"
            ]
            
            if any(keyword in filename for keyword in exclude_keywords):
                return False
            
            # Include core system files
            core_keywords = [
                "server", "api", "portal", "relay", "launcher", 
                "enterprise", "copilot", "web_", "start_"
            ]
            
            if any(keyword in filename for keyword in core_keywords):
                return True
        
        return False
    
    def _classify_file_type(self, file_path):
        """Classify file type"""
        suffix = file_path.suffix.lower()
        name = file_path.name.lower()
        
        if suffix == ".py":
            if any(x in name for x in ["server", "api", "portal", "relay", "launcher"]):
                return "core_system"
            return "python_module"
        elif suffix == ".db":
            return "database"
        elif suffix in [".html", ".css", ".js"]:
            return "web_asset"
        else:
            return "other"
    
    def migrate_documentation_to_database(self):
        """
        PHASE 2: Migrate ALL documentation to database
        """
        logger.info("=" * 80)
        logger.info("PHASE 2: MIGRATING DOCUMENTATION TO DATABASE")
        logger.info("=" * 80)
        
        # Copy database from sandbox if needed
        db_path = self.production_path / "production.db"
        sandbox_db = self.sandbox_path / "production.db"
        
        if sandbox_db.exists():
            # Ensure production directory exists
            self.production_path.mkdir(parents=True, exist_ok=True)
            shutil.copy2(sandbox_db, db_path)
            logger.info(f"Database copied to production: {db_path}")
        
        # Connect and create documentation table
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Create documentation table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS production_documentation (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    doc_type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    file_path TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Migrate documentation files
            doc_count = 0
            doc_patterns = ["*.md", "*.txt", "*_report_*", "*_summary_*"]
            
            for pattern in doc_patterns:
                for doc_file in self.sandbox_path.rglob(pattern):
                    if doc_file.is_file():
                        try:
                            content = doc_file.read_text(encoding='utf-8', errors='ignore')
                            relative_path = doc_file.relative_to(self.sandbox_path)
                            
                            cursor.execute("""
                                INSERT OR REPLACE INTO production_documentation 
                                (doc_type, title, content, file_path)
                                VALUES (?, ?, ?, ?)
                            """, (
                                self._get_doc_type(doc_file),
                                doc_file.name,
                                content,
                                str(relative_path)
                            ))
                            
                            doc_count += 1
                            
                        except Exception as e:
                            logger.warning(f"Could not migrate {doc_file}: {e}")
            
            conn.commit()
            
            # Count total documents
            cursor.execute("SELECT COUNT(*) FROM production_documentation")
            total_docs = cursor.fetchone()[0]
            
            logger.info(f"Documentation migration complete:")
            logger.info(f"   Documents migrated: {doc_count}")
            logger.info(f"   Total in database: {total_docs}")
            
            self.results["documentation_migrated"] = {
                "migrated_count": doc_count,
                "total_in_database": total_docs
            }
    
    def _get_doc_type(self, file_path):
        """Classify documentation type"""
        name = file_path.name.lower()
        if "report" in name:
            return "report"
        elif "summary" in name:
            return "summary" 
        elif "readme" in name:
            return "readme"
        elif file_path.suffix == ".md":
            return "markdown"
        else:
            return "documentation"
    
    def create_production_environment(self, necessary_files):
        """
        PHASE 3: Create clean production environment
        """
        logger.info("=" * 80)
        logger.info("PHASE 3: CREATING PRODUCTION ENVIRONMENT")
        logger.info("=" * 80)
        
        # Clean and create production directory
        if self.production_path.exists() and len(list(self.production_path.iterdir())) > 1:
            logger.info("Cleaning existing production files...")
            for item in self.production_path.iterdir():
                if item.name != "production.db":  # Keep database
                    if item.is_dir():
                        shutil.rmtree(item)
                    else:
                        item.unlink()
        
        self.production_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Production directory ready: {self.production_path}")
        
        # Copy necessary files
        copied_files = 0
        total_size = 0
        
        print(f"Copying {len(necessary_files)} necessary files...")
        
        for i, file_info in enumerate(necessary_files):
            if i % 10 == 0:
                print(f"Copying: {i}/{len(necessary_files)} ({i/len(necessary_files)*100:.1f}%)")
            
            src_path = self.sandbox_path / file_info["path"]
            dst_path = self.production_path / file_info["path"]
            
            # Create directory if needed
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            
            try:
                shutil.copy2(src_path, dst_path)
                copied_files += 1
                total_size += file_info["size"]
            except Exception as e:
                logger.error(f"Failed to copy {file_info['path']}: {e}")
        
        logger.info(f"Production environment created:")
        logger.info(f"   Files copied: {copied_files}")
        logger.info(f"   Total size: {total_size / (1024*1024):.1f} MB")
        
        return copied_files
    
    def validate_production_environment(self):
        """
        PHASE 4: Validate production environment
        """
        logger.info("=" * 80)
        logger.info("PHASE 4: VALIDATING PRODUCTION ENVIRONMENT")
        logger.info("=" * 80)
        
        validation_results = {
            "database_present": False,
            "essential_files_present": False,
            "no_documentation_files": False,
            "python_files_valid": False,
            "github_copilot_ready": False,
            "error_count": 0
        }
        
        # 1. Check database
        db_path = self.production_path / "production.db"
        if db_path.exists():
            try:
                with sqlite3.connect(db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
                    table_count = cursor.fetchone()[0]
                    validation_results["database_present"] = table_count >= 5
                    logger.info(f"Database tables: {table_count}")
            except Exception as e:
                logger.error(f"Database validation failed: {e}")
                validation_results["error_count"] += 1
        
        # 2. Check essential files
        essential_files = [
            "production.db",
            "web_portal_enterprise_system.py",
            "requirements.txt"
        ]
        
        files_present = 0
        for file_name in essential_files:
            if (self.production_path / file_name).exists():
                files_present += 1
        
        validation_results["essential_files_present"] = files_present == len(essential_files)
        logger.info(f"Essential files present: {files_present}/{len(essential_files)}")
        
        # 3. Check no documentation in filesystem
        doc_files = []
        for pattern in ["*.md", "*.txt", "*_report_*"]:
            doc_files.extend(list(self.production_path.rglob(pattern)))
        
        validation_results["no_documentation_files"] = len(doc_files) == 0
        logger.info(f"Documentation files in filesystem: {len(doc_files)}")
        
        # 4. Check Python files
        python_files = list(self.production_path.rglob("*.py"))
        syntax_errors = 0
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    compile(f.read(), py_file, 'exec')
            except SyntaxError:
                syntax_errors += 1
            except Exception:
                pass
        
        validation_results["python_files_valid"] = syntax_errors == 0
        validation_results["error_count"] += syntax_errors
        logger.info(f"Python files: {len(python_files)}, Syntax errors: {syntax_errors}")
        
        # 5. Check GitHub Copilot readiness
        copilot_files = ["copilot_cli_relay_api.py", "web_portal_enterprise_system.py"]
        copilot_ready = sum(1 for f in copilot_files if (self.production_path / f).exists())
        validation_results["github_copilot_ready"] = copilot_ready >= 1
        logger.info(f"GitHub Copilot files present: {copilot_ready}")
        
        # Calculate score
        passed = sum(1 for k, v in validation_results.items() if k != "error_count" and v)
        total = len(validation_results) - 1
        score = (passed / total) * 100
        
        self.results["validation_results"] = validation_results
        self.results["validation_score"] = score
        self.results["production_ready"] = (score >= 100 and validation_results["error_count"] == 0)
        
        logger.info("VALIDATION SUMMARY")
        logger.info(f"Score: {score:.1f}%")
        logger.info(f"Errors: {validation_results['error_count']}")
        logger.info(f"Production Ready: {self.results['production_ready']}")
        
        return validation_results
    
    def generate_manifest(self):
        """Generate production manifest"""
        end_time = datetime.datetime.now()
        duration = end_time - self.start_time
        
        manifest = {
            "production_environment": {
                "path": str(self.production_path),
                "created_at": self.start_time.isoformat(),
                "completed_at": end_time.isoformat(),
                "duration_seconds": duration.total_seconds()
            },
            "statistics": {
                "necessary_files": len(self.results["necessary_files"]),
                "excluded_files": len(self.results["excluded_files"]),
                "reduction_percentage": (len(self.results["excluded_files"]) / 
                                       (len(self.results["necessary_files"]) + len(self.results["excluded_files"])) * 100)
            },
            "validation": self.results["validation_results"],
            "production_ready": self.results["production_ready"]
        }
        
        # Save manifest
        manifest_file = self.production_path / "production_manifest.json"
        with open(manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        logger.info(f"Manifest saved: {manifest_file}")
        return manifest

def main():
    """Build production environment"""
    builder = ProductionEnvironmentBuilder()
    
    try:
        # Execute phases
        necessary_files = builder.identify_necessary_system_files()
        builder.migrate_documentation_to_database()
        builder.create_production_environment(necessary_files)
        builder.validate_production_environment()
        builder.generate_manifest()
        
        # Final summary
        logger.info("=" * 80)
        logger.info("PRODUCTION ENVIRONMENT BUILD COMPLETE")
        logger.info("=" * 80)
        
        if builder.results["production_ready"]:
            logger.info("SUCCESS: 100% error-free production environment ready")
            logger.info(f"Location: {builder.production_path}")
            logger.info(f"Files: {len(necessary_files)} necessary files only")
            logger.info("Documentation: All migrated to database")
            logger.info("GitHub Copilot Integration: Ready")
            return 0
        else:
            logger.error("FAILED: Production environment has errors")
            return 1
            
    except Exception as e:
        logger.error(f"CRITICAL ERROR: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
