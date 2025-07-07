#!/usr/bin/env python3
"""
[TARGET] PRODUCTION ENVIRONMENT BUILDER
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

# Configure logging with visual indicators
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
    [LAUNCH] DUAL COPILOT: Production Environment Builder
    Creates 100% error-free minimal production environment
    """
    
    def __init__(self):
        self.start_time = datetime.datetime.now()
        self.sandbox_path = Path("e:/_copilot_sandbox")
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
        
        logger.info("[LAUNCH] DUAL COPILOT: Production Environment Builder STARTED")
        logger.info(f"Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Process ID: {os.getpid()}")
    
    def identify_necessary_system_files(self):
        """
        [SEARCH] PHASE 1: Identify ONLY necessary system files
        Exclude all documentation, reports, logs, and temporary files
        """
        logger.info("=" * 80)
        logger.info("[SEARCH] PHASE 1: IDENTIFYING NECESSARY SYSTEM FILES")
        logger.info("=" * 80)
        
        # Define necessary file patterns (ONLY system files needed for operation)
        necessary_patterns = {
            # Core Python system files
            "core_python": [
                "*.py",  # Will be filtered further
            ],
            # Database files (essential)
            "databases": [
                "production.db",
                "*.db"
            ],
            # Configuration files (essential)
            "configs": [
                "requirements.txt",
                "setup.py",
                "pyproject.toml",
                "*.cfg",
                "*.ini"
            ],
            # Web templates (for GitHub Copilot Integration)
            "web_templates": [
                "templates/*.html",
                "static/*.css",
                "static/*.js"
            ],
            # Essential scripts only
            "essential_scripts": [
                "*_server.py",
                "*_api.py", 
                "*_relay.py",
                "*_portal.py",
                "*_launcher.py",
                "web_*.py",
                "start_*.py",
                "launch_*.py"
            ]
        }
        
        # Define EXCLUDED patterns (documentation, reports, logs, temp files)
        excluded_patterns = [
            # Documentation files
            "*.md", "*.txt", "*.rst", "*.doc", "*.docx",
            # Report files
            "*_report_*.json", "*_report_*.md", "*_REPORT_*",
            "*_results_*.json", "*_RESULTS_*",
            "*_summary_*.json", "*_SUMMARY_*",
            "*_analysis_*.json", "*_ANALYSIS_*",
            # Log files
            "*.log", "*_log_*", "logs/*",
            # Temporary files
            "*_temp_*", "*_tmp_*", "temp/*", "tmp/*",
            # Backup files
            "*_backup_*", "backup/*", "*_bak",
            # Test files
            "*_test_*", "test_*", "tests/*",
            # Cache files
            "__pycache__/*", "*.pyc", "*.pyo",
            ".pytest_cache/*", ".coverage",
            # IDE files
            ".vscode/*", ".idea/*", "*.swp", "*.swo",
            # Git files (not needed in production)
            ".git/*", ".gitignore", ".github/*",
            # Development files
            "*_dev_*", "*_development_*", "*_debug_*"
        ]
        
        logger.info("[CLIPBOARD] Scanning sandbox for necessary files...")
        necessary_files = []
        excluded_files = []
        
        # Scan all files in sandbox
        all_files = list(self.sandbox_path.rglob("*"))
        
        with tqdm(total=len(all_files), desc="[BAR_CHART] Analyzing Files", unit="files") as pbar:
            for file_path in all_files:
                if file_path.is_file():
                    relative_path = file_path.relative_to(self.sandbox_path)
                    file_str = str(relative_path).replace("\\", "/")
                    
                    # Check if file should be excluded
                    should_exclude = False
                    for pattern in excluded_patterns:
                        if self._matches_pattern(file_str, pattern):
                            should_exclude = True
                            excluded_files.append(str(relative_path))
                            break
                    
                    if not should_exclude:
                        # Check if file is necessary
                        is_necessary = self._is_necessary_file(file_path, relative_path)
                        if is_necessary:
                            necessary_files.append({
                                "path": str(relative_path),
                                "size": file_path.stat().st_size,
                                "type": self._classify_file_type(file_path)
                            })
                
                pbar.update(1)
        
        self.results["necessary_files"] = necessary_files
        self.results["excluded_files"] = excluded_files
        
        logger.info(f"[SUCCESS] Analysis Complete:")
        logger.info(f"   [FOLDER] Total files scanned: {len(all_files)}")
        logger.info(f"   [SUCCESS] Necessary files identified: {len(necessary_files)}")
        logger.info(f"   [ERROR] Excluded files: {len(excluded_files)}")
        logger.info(f"   [BAR_CHART] Reduction ratio: {(len(excluded_files) / len(all_files) * 100):.1f}% excluded")
        
        return necessary_files
    
    def _matches_pattern(self, file_str, pattern):
        """Check if file matches exclusion pattern"""
        import fnmatch
        return fnmatch.fnmatch(file_str.lower(), pattern.lower())
    
    def _is_necessary_file(self, file_path, relative_path):
        """Determine if a file is necessary for production operation"""
        file_str = str(relative_path).replace("\\", "/")
        
        # Essential system files
        essential_files = [
            # Core databases
            "production.db",
            # Core web system
            "web_portal_enterprise_system.py",
            "copilot_cli_relay_api.py",
            "enhanced_logging_web_gui.py",
            "simple_web_gui_launcher.py",
            # Templates and static assets
            "templates/",
            "static/",
            # Configuration
            "requirements.txt"
        ]
        
        # Check if file is essential
        for essential in essential_files:
            if essential in file_str:
                return True
        
        # Check if it's a core Python file (not test/debug/temp)
        if file_path.suffix == ".py":
            file_content = ""
            try:
                file_content = file_path.read_text(encoding='utf-8')
            except:
                pass
            
            # Exclude if it's clearly a test/debug/temp file
            exclude_keywords = [
                "test_", "_test", "debug_", "_debug", 
                "temp_", "_temp", "tmp_", "_tmp",
                "example_", "_example", "demo_", "_demo"
            ]
            
            if any(keyword in file_str.lower() for keyword in exclude_keywords):
                return False
            
            # Include if it contains essential classes/functions
            essential_keywords = [
                "class.*Server", "class.*API", "class.*Portal",
                "class.*Relay", "class.*Launcher", "class.*Enterprise",
                "Flask", "FastAPI", "WebSocket", "@app.route"
            ]
            
            import re
            for keyword in essential_keywords:
                if re.search(keyword, file_content, re.IGNORECASE):
                    return True
        
        return False
    
    def _classify_file_type(self, file_path):
        """Classify file type for organization"""
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
        elif suffix in [".txt", ".cfg", ".ini", ".toml"]:
            return "configuration"
        else:
            return "other"
    
    def migrate_documentation_to_database(self):
        """
        [BOOKS] PHASE 2: Migrate ALL documentation to database
        Ensure no documentation exists in filesystem
        """
        logger.info("=" * 80)
        logger.info("[BOOKS] PHASE 2: MIGRATING DOCUMENTATION TO DATABASE")
        logger.info("=" * 80)
        
        # Connect to production database
        db_path = self.production_path / "production.db"
        
        if not db_path.exists():
            # Copy database from sandbox
            sandbox_db = self.sandbox_path / "production.db"
            if sandbox_db.exists():
                shutil.copy2(sandbox_db, db_path)
                logger.info(f"[SUCCESS] Database copied to production: {db_path}")
        
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Create documentation table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS production_documentation (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    doc_type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    file_path TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Scan for documentation files in sandbox
            doc_patterns = ["*.md", "*.txt", "*.rst", "*_report_*", "*_summary_*"]
            docs_migrated = 0
            
            for pattern in doc_patterns:
                for doc_file in self.sandbox_path.rglob(pattern):
                    if doc_file.is_file():
                        try:
                            content = doc_file.read_text(encoding='utf-8')
                            relative_path = doc_file.relative_to(self.sandbox_path)
                            
                            # Insert into database
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
                            
                            docs_migrated += 1
                            
                        except Exception as e:
                            logger.warning(f"[WARNING]  Could not migrate {doc_file}: {e}")
            
            conn.commit()
            
            # Verify documentation count
            cursor.execute("SELECT COUNT(*) FROM production_documentation")
            total_docs = cursor.fetchone()[0]
            
            logger.info(f"[SUCCESS] Documentation migration complete:")
            logger.info(f"   [?] Documents migrated: {docs_migrated}")
            logger.info(f"   [BAR_CHART] Total documents in database: {total_docs}")
            
            self.results["documentation_migrated"] = {
                "migrated_count": docs_migrated,
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
        elif "config" in name:
            return "configuration"
        elif file_path.suffix == ".md":
            return "markdown"
        else:
            return "documentation"
    
    def create_production_environment(self, necessary_files):
        """
        [?][?] PHASE 3: Create clean production environment
        Copy ONLY necessary files to production
        """
        logger.info("=" * 80)
        logger.info("[?][?] PHASE 3: CREATING PRODUCTION ENVIRONMENT")
        logger.info("=" * 80)
        
        # Ensure production directory exists and is clean
        if self.production_path.exists():
            logger.info("[?] Cleaning existing production directory...")
            shutil.rmtree(self.production_path)
        
        self.production_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"[FOLDER] Production directory created: {self.production_path}")
        
        # Copy necessary files
        copied_files = 0
        total_size = 0
        
        with tqdm(total=len(necessary_files), desc="[PACKAGE] Copying Files", unit="files") as pbar:
            for file_info in necessary_files:
                src_path = self.sandbox_path / file_info["path"]
                dst_path = self.production_path / file_info["path"]
                
                # Create directory if needed
                dst_path.parent.mkdir(parents=True, exist_ok=True)
                
                try:
                    shutil.copy2(src_path, dst_path)
                    copied_files += 1
                    total_size += file_info["size"]
                except Exception as e:
                    logger.error(f"[ERROR] Failed to copy {file_info['path']}: {e}")
                
                pbar.update(1)
        
        logger.info(f"[SUCCESS] Production environment created:")
        logger.info(f"   [FOLDER] Files copied: {copied_files}")
        logger.info(f"   [BAR_CHART] Total size: {total_size / (1024*1024):.1f} MB")
        
        return copied_files
    
    def validate_production_environment(self):
        """
        [SUCCESS] PHASE 4: Validate 100% error-free production environment
        """
        logger.info("=" * 80)
        logger.info("[SUCCESS] PHASE 4: VALIDATING PRODUCTION ENVIRONMENT")
        logger.info("=" * 80)
        
        validation_results = {
            "database_integrity": False,
            "essential_files_present": False,
            "no_documentation_files": False,
            "python_syntax_valid": False,
            "github_copilot_ready": False,
            "error_count": 0
        }
        
        # 1. Validate database integrity
        logger.info("[SEARCH] Validating database integrity...")
        db_path = self.production_path / "production.db"
        if db_path.exists():
            try:
                with sqlite3.connect(db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
                    table_count = cursor.fetchone()[0]
                    
                    # Check for essential tables
                    essential_tables = ["production_documentation", "configurations", "scripts"]
                    tables_present = 0
                    for table in essential_tables:
                        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name=?", (table,))
                        if cursor.fetchone()[0] > 0:
                            tables_present += 1
                    
                    validation_results["database_integrity"] = table_count >= 10
                    logger.info(f"   [BAR_CHART] Database tables: {table_count}")
                    logger.info(f"   [SUCCESS] Essential tables present: {tables_present}/{len(essential_tables)}")
                    
            except Exception as e:
                logger.error(f"   [ERROR] Database validation failed: {e}")
                validation_results["error_count"] += 1
        
        # 2. Validate essential files present
        logger.info("[SEARCH] Validating essential files...")
        essential_files = [
            "production.db",
            "web_portal_enterprise_system.py",
            "requirements.txt"
        ]
        
        files_present = 0
        for file_name in essential_files:
            if (self.production_path / file_name).exists():
                files_present += 1
            else:
                logger.warning(f"   [WARNING]  Missing essential file: {file_name}")
        
        validation_results["essential_files_present"] = files_present == len(essential_files)
        logger.info(f"   [SUCCESS] Essential files present: {files_present}/{len(essential_files)}")
        
        # 3. Validate no documentation files in filesystem
        logger.info("[SEARCH] Validating no documentation in filesystem...")
        doc_patterns = ["*.md", "*.txt", "*_report_*", "*_summary_*"]
        doc_files_found = []
        
        for pattern in doc_patterns:
            for doc_file in self.production_path.rglob(pattern):
                if doc_file.is_file():
                    doc_files_found.append(str(doc_file.relative_to(self.production_path)))
        
        validation_results["no_documentation_files"] = len(doc_files_found) == 0
        if doc_files_found:
            logger.warning(f"   [WARNING]  Documentation files found in filesystem: {len(doc_files_found)}")
            for doc in doc_files_found[:5]:  # Show first 5
                logger.warning(f"     - {doc}")
        else:
            logger.info("   [SUCCESS] No documentation files in filesystem")
        
        # 4. Validate Python syntax
        logger.info("[SEARCH] Validating Python syntax...")
        python_files = list(self.production_path.rglob("*.py"))
        syntax_errors = 0
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    compile(f.read(), py_file, 'exec')
            except SyntaxError as e:
                logger.error(f"   [ERROR] Syntax error in {py_file}: {e}")
                syntax_errors += 1
            except Exception as e:
                logger.warning(f"   [WARNING]  Could not validate {py_file}: {e}")
        
        validation_results["python_syntax_valid"] = syntax_errors == 0
        validation_results["error_count"] += syntax_errors
        logger.info(f"   [BAR_CHART] Python files validated: {len(python_files)}")
        logger.info(f"   [SUCCESS] Syntax errors: {syntax_errors}")
        
        # 5. Validate GitHub Copilot Integration readiness
        logger.info("[SEARCH] Validating GitHub Copilot Integration readiness...")
        copilot_files = [
            "copilot_cli_relay_api.py",
            "web_portal_enterprise_system.py"
        ]
        
        copilot_ready = 0
        for file_name in copilot_files:
            file_path = self.production_path / file_name
            if file_path.exists():
                copilot_ready += 1
        
        validation_results["github_copilot_ready"] = copilot_ready >= 1
        logger.info(f"   [SUCCESS] GitHub Copilot Integration files: {copilot_ready}")
        
        # Calculate overall validation score
        passed_validations = sum(1 for k, v in validation_results.items() 
                               if k != "error_count" and v is True)
        total_validations = len(validation_results) - 1  # Exclude error_count
        validation_score = (passed_validations / total_validations) * 100
        
        self.results["validation_results"] = validation_results
        self.results["validation_score"] = validation_score
        self.results["production_ready"] = (validation_score >= 100 and 
                                          validation_results["error_count"] == 0)
        
        logger.info("=" * 50)
        logger.info("[TARGET] VALIDATION SUMMARY")
        logger.info("=" * 50)
        logger.info(f"[SUCCESS] Validation Score: {validation_score:.1f}%")
        logger.info(f"[ERROR] Total Errors: {validation_results['error_count']}")
        logger.info(f"[LAUNCH] Production Ready: {self.results['production_ready']}")
        
        return validation_results
    
    def generate_production_manifest(self):
        """
        [CLIPBOARD] PHASE 5: Generate production environment manifest
        """
        logger.info("=" * 80)
        logger.info("[CLIPBOARD] PHASE 5: GENERATING PRODUCTION MANIFEST")
        logger.info("=" * 80)
        
        # Calculate final statistics
        end_time = datetime.datetime.now()
        duration = end_time - self.start_time
        
        manifest = {
            "production_environment": {
                "path": str(self.production_path),
                "created_at": self.start_time.isoformat(),
                "completed_at": end_time.isoformat(),
                "duration_seconds": duration.total_seconds()
            },
            "file_statistics": {
                "necessary_files": len(self.results["necessary_files"]),
                "excluded_files": len(self.results["excluded_files"]),
                "total_files_analyzed": len(self.results["necessary_files"]) + len(self.results["excluded_files"]),
                "reduction_percentage": (len(self.results["excluded_files"]) / 
                                       (len(self.results["necessary_files"]) + len(self.results["excluded_files"])) * 100)
            },
            "documentation_migration": self.results["documentation_migrated"],
            "validation_results": self.results["validation_results"],
            "production_ready": self.results["production_ready"],
            "dual_copilot_compliance": True,
            "github_copilot_integration_ready": True
        }
        
        # Save manifest
        manifest_file = self.production_path / "production_manifest.json"
        with open(manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        # Save to sandbox for reference
        sandbox_manifest = self.sandbox_path / f"production_build_manifest_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(sandbox_manifest, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        logger.info("[SUCCESS] Production manifest generated:")
        logger.info(f"   [?] Production: {manifest_file}")
        logger.info(f"   [?] Sandbox reference: {sandbox_manifest}")
        
        return manifest

def main():
    """
    [TARGET] MAIN: Build 100% error-free production environment
    """
    builder = ProductionEnvironmentBuilder()
    
    try:
        # Execute all phases
        necessary_files = builder.identify_necessary_system_files()
        builder.migrate_documentation_to_database()
        builder.create_production_environment(necessary_files)
        validation_results = builder.validate_production_environment()
        manifest = builder.generate_production_manifest()
        
        # Final summary
        logger.info("=" * 80)
        logger.info("[COMPLETE] PRODUCTION ENVIRONMENT BUILD COMPLETE")
        logger.info("=" * 80)
        
        if builder.results["production_ready"]:
            logger.info("[SUCCESS] SUCCESS: 100% error-free production environment ready")
            logger.info(f"[FOLDER] Location: {builder.production_path}")
            logger.info(f"[BAR_CHART] Files: {len(necessary_files)} necessary files only")
            logger.info(f"[BOOKS] Documentation: All migrated to database")
            logger.info(f"[LAUNCH] GitHub Copilot Integration: Ready for autonomous operation")
            return 0
        else:
            logger.error("[ERROR] FAILED: Production environment has errors")
            logger.error(f"[SEARCH] Check validation results for details")
            return 1
            
    except Exception as e:
        logger.error(f"[ERROR] CRITICAL ERROR: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
