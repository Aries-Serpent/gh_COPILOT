#!/usr/bin/env python3
"""
REFINED PRODUCTION ENVIRONMENT BUILDER
Creates 100% error-free minimal production environment with EXACT necessary files
"""

import os
import sys
import json
import shutil
import sqlite3
import datetime
from pathlib import Path

class RefinedProductionBuilder:
    """Creates minimal production environment with only essential operational files"""
    
    def __init__(self):
        self.start_time = datetime.datetime.now()
        self.sandbox_path = Path("e:/_copilot_sandbox")
        self.production_path = Path("e:/_copilot_production-001")
        
        print("REFINED PRODUCTION BUILDER STARTED")
        print(f"Start Time: {self.start_time}")
        print(f"Sandbox: {self.sandbox_path}")
        print(f"Production: {self.production_path}")
    
    def get_essential_files(self):
        """Define EXACT list of essential files needed for production operation"""
        
        # CORE ESSENTIAL FILES - Minimal set for 100% operation
        essential_files = [
            # 1. DATABASE (critical)
            "production.db",
            
            # 2. CORE WEB SYSTEM (critical for GitHub Copilot Integration)
            "web_portal_enterprise_system.py",
            "start_web_portal.py", 
            "simple_web_gui_launcher.py",
            
            # 3. GITHUB COPILOT INTEGRATION (critical)
            "copilot_cli_relay_api.py",
            "enhanced_logging_web_gui.py",
            
            # 4. CONFIGURATION (critical)
            "requirements.txt",
            
            # 5. WEB TEMPLATES (required for web interface)
            "templates/dashboard.html",
            "templates/certification.html", 
            "templates/database.html",
            "templates/deployment_wizard.html",
            "templates/deployment_dashboard.html",
            
            # 6. STATIC ASSETS (required for web interface)
            "static/css/style.css",
            "static/js/portal.js",
            
            # 7. LAUNCH SCRIPTS (for system startup)
            "launch_web_portal.ps1"
        ]
        
        print(f"Essential files defined: {len(essential_files)}")
        return essential_files
    
    def verify_essential_files_exist(self, essential_files):
        """Verify all essential files exist in sandbox before copying"""
        
        print("Verifying essential files exist in sandbox...")
        
        existing_files = []
        missing_files = []
        
        for file_path in essential_files:
            full_path = self.sandbox_path / file_path
            if full_path.exists():
                existing_files.append(file_path)
                print(f"  FOUND: {file_path}")
            else:
                missing_files.append(file_path)
                print(f"  MISSING: {file_path}")
        
        print(f"Essential files verification:")
        print(f"  Found: {len(existing_files)}")
        print(f"  Missing: {len(missing_files)}")
        
        if missing_files:
            print("WARNING: Some essential files are missing!")
            # Try to find alternatives
            self.find_alternative_files(missing_files)
        
        return existing_files, missing_files
    
    def find_alternative_files(self, missing_files):
        """Find alternative files for missing essential files"""
        
        print("Searching for alternative files...")
        
        alternatives = {
            "copilot_cli_relay_api.py": ["*copilot*relay*.py", "*cli*relay*.py"],
            "web_portal_enterprise_system.py": ["*web*portal*.py", "*portal*enterprise*.py"],
            "start_web_portal.py": ["*start*web*.py", "*launch*portal*.py"],
            "enhanced_logging_web_gui.py": ["*logging*web*.py", "*web*gui*.py"]
        }
        
        for missing_file in missing_files:
            if missing_file in alternatives:
                print(f"  Searching alternatives for {missing_file}:")
                for pattern in alternatives[missing_file]:
                    matches = list(self.sandbox_path.rglob(pattern))
                    if matches:
                        print(f"    Alternative found: {matches[0].relative_to(self.sandbox_path)}")
                        break
    
    def create_clean_production_environment(self, essential_files):
        """Create completely clean production environment with only essential files"""
        
        print("Creating clean production environment...")
        
        # Remove existing production directory completely
        if self.production_path.exists():
            print("Removing existing production directory...")
            shutil.rmtree(self.production_path)
        
        # Create fresh production directory
        self.production_path.mkdir(parents=True, exist_ok=True)
        print(f"Created fresh production directory: {self.production_path}")
        
        # Copy only essential files
        copied_files = 0
        failed_files = []
        
        print("Copying essential files...")
        
        for file_path in essential_files:
            src_path = self.sandbox_path / file_path
            dst_path = self.production_path / file_path
            
            if src_path.exists():
                try:
                    # Create directory if needed
                    dst_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Copy file
                    shutil.copy2(src_path, dst_path)
                    copied_files += 1
                    print(f"  COPIED: {file_path}")
                    
                except Exception as e:
                    failed_files.append(f"{file_path}: {e}")
                    print(f"  FAILED: {file_path} - {e}")
            else:
                failed_files.append(f"{file_path}: Not found")
                print(f"  NOT FOUND: {file_path}")
        
        print(f"File copying complete:")
        print(f"  Successfully copied: {copied_files}")
        print(f"  Failed: {len(failed_files)}")
        
        return copied_files, failed_files
    
    def migrate_all_documentation_to_database(self):
        """Migrate ALL documentation from filesystem to database"""
        
        print("Migrating documentation to database...")
        
        # Connect to production database
        db_path = self.production_path / "production.db"
        
        if not db_path.exists():
            # Copy database from sandbox
            sandbox_db = self.sandbox_path / "production.db"
            if sandbox_db.exists():
                shutil.copy2(sandbox_db, db_path)
                print(f"Database copied to production: {db_path}")
            else:
                print("ERROR: production.db not found in sandbox!")
                return 0
        
        # Open database and create documentation table
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Create comprehensive documentation table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS all_documentation (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    doc_category TEXT NOT NULL,
                    doc_title TEXT NOT NULL,
                    doc_content TEXT NOT NULL,
                    original_path TEXT,
                    file_size INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Migrate ALL documentation files from sandbox
            doc_patterns = [
                "*.md", "*.txt", "*.rst", "*.doc", 
                "*_report_*", "*_REPORT_*", 
                "*_summary_*", "*_SUMMARY_*",
                "*_analysis_*", "*_ANALYSIS_*",
                "*_results_*", "*_RESULTS_*"
            ]
            
            total_docs = 0
            total_size = 0
            
            for pattern in doc_patterns:
                for doc_file in self.sandbox_path.rglob(pattern):
                    if doc_file.is_file():
                        try:
                            content = doc_file.read_text(encoding='utf-8', errors='ignore')
                            relative_path = doc_file.relative_to(self.sandbox_path)
                            file_size = doc_file.stat().st_size
                            
                            # Insert into database
                            cursor.execute("""
                                INSERT OR REPLACE INTO all_documentation 
                                (doc_category, doc_title, doc_content, original_path, file_size)
                                VALUES (?, ?, ?, ?, ?)
                            """, (
                                self._categorize_document(doc_file),
                                doc_file.name,
                                content,
                                str(relative_path),
                                file_size
                            ))
                            
                            total_docs += 1
                            total_size += file_size
                            
                            if total_docs % 100 == 0:
                                print(f"  Migrated {total_docs} documents...")
                            
                        except Exception as e:
                            print(f"  WARNING: Could not migrate {doc_file}: {e}")
            
            conn.commit()
            
            # Verify migration
            cursor.execute("SELECT COUNT(*), SUM(file_size) FROM all_documentation")
            db_docs, db_size = cursor.fetchone()
            
            print(f"Documentation migration complete:")
            print(f"  Documents migrated: {total_docs}")
            print(f"  Total size: {total_size / (1024*1024):.1f} MB")
            print(f"  Documents in database: {db_docs}")
            print(f"  Database size: {(db_size or 0) / (1024*1024):.1f} MB")
            
            return total_docs
    
    def _categorize_document(self, file_path):
        """Categorize document type"""
        name = file_path.name.lower()
        if "report" in name:
            return "reports"
        elif "summary" in name:
            return "summaries"
        elif "analysis" in name:
            return "analysis"
        elif "results" in name:
            return "results"
        elif "readme" in name:
            return "readme"
        elif file_path.suffix == ".md":
            return "markdown"
        else:
            return "documentation"
    
    def validate_production_environment(self):
        """Comprehensive validation of production environment"""
        
        print("Validating production environment...")
        
        validation = {
            "database_present": False,
            "essential_files_present": False,
            "no_documentation_files": False,
            "python_syntax_valid": False,
            "github_copilot_ready": False,
            "web_templates_present": False,
            "static_assets_present": False,
            "error_count": 0,
            "validation_details": []
        }
        
        # 1. Database validation
        db_path = self.production_path / "production.db"
        if db_path.exists():
            try:
                with sqlite3.connect(db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
                    table_count = cursor.fetchone()[0]
                    
                    validation["database_present"] = table_count >= 5
                    validation["validation_details"].append(f"Database tables: {table_count}")
                    
                    # Check documentation table
                    cursor.execute("SELECT COUNT(*) FROM all_documentation")
                    doc_count = cursor.fetchone()[0]
                    validation["validation_details"].append(f"Documents in database: {doc_count}")
                    
            except Exception as e:
                validation["error_count"] += 1
                validation["validation_details"].append(f"Database error: {e}")
        
        # 2. Essential files validation
        essential_core = [
            "production.db",
            "web_portal_enterprise_system.py", 
            "requirements.txt"
        ]
        
        present_count = 0
        for file_name in essential_core:
            if (self.production_path / file_name).exists():
                present_count += 1
                validation["validation_details"].append(f"Essential file present: {file_name}")
            else:
                validation["validation_details"].append(f"Essential file MISSING: {file_name}")
        
        validation["essential_files_present"] = present_count == len(essential_core)
        
        # 3. No documentation files in filesystem
        doc_files = []
        for pattern in ["*.md", "*.txt", "*_report_*"]:
            doc_files.extend(list(self.production_path.rglob(pattern)))
        
        validation["no_documentation_files"] = len(doc_files) == 0
        validation["validation_details"].append(f"Documentation files in filesystem: {len(doc_files)}")
        
        # 4. Python syntax validation
        python_files = list(self.production_path.rglob("*.py"))
        syntax_errors = 0
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    compile(f.read(), py_file, 'exec')
            except SyntaxError as e:
                syntax_errors += 1
                validation["validation_details"].append(f"Syntax error in {py_file.name}: {e}")
            except Exception:
                pass
        
        validation["python_syntax_valid"] = syntax_errors == 0
        validation["error_count"] += syntax_errors
        validation["validation_details"].append(f"Python files: {len(python_files)}, Syntax errors: {syntax_errors}")
        
        # 5. GitHub Copilot Integration readiness
        copilot_files = [
            "web_portal_enterprise_system.py",
            "copilot_cli_relay_api.py"
        ]
        
        copilot_present = 0
        for file_name in copilot_files:
            if (self.production_path / file_name).exists():
                copilot_present += 1
        
        validation["github_copilot_ready"] = copilot_present >= 1
        validation["validation_details"].append(f"GitHub Copilot files present: {copilot_present}/{len(copilot_files)}")
        
        # 6. Web templates validation
        template_files = list(self.production_path.glob("templates/*.html"))
        validation["web_templates_present"] = len(template_files) >= 3
        validation["validation_details"].append(f"Web templates: {len(template_files)}")
        
        # 7. Static assets validation
        css_files = list(self.production_path.glob("static/css/*.css"))
        js_files = list(self.production_path.glob("static/js/*.js"))
        validation["static_assets_present"] = len(css_files) >= 1 and len(js_files) >= 1
        validation["validation_details"].append(f"Static assets: {len(css_files)} CSS, {len(js_files)} JS")
        
        # Calculate overall score
        criteria = [
            "database_present", "essential_files_present", "no_documentation_files",
            "python_syntax_valid", "github_copilot_ready", "web_templates_present", 
            "static_assets_present"
        ]
        
        passed = sum(1 for criterion in criteria if validation[criterion])
        score = (passed / len(criteria)) * 100
        
        production_ready = (score >= 100 and validation["error_count"] == 0)
        
        print("VALIDATION RESULTS:")
        print(f"  Score: {score:.1f}% ({passed}/{len(criteria)} criteria passed)")
        print(f"  Errors: {validation['error_count']}")
        print(f"  Production Ready: {production_ready}")
        
        print("\nValidation Details:")
        for detail in validation["validation_details"]:
            print(f"  - {detail}")
        
        return validation, score, production_ready
    
    def generate_final_manifest(self, validation, score, production_ready):
        """Generate final production manifest"""
        
        end_time = datetime.datetime.now()
        duration = end_time - self.start_time
        
        # Count files in production
        all_files = list(self.production_path.rglob("*"))
        file_count = len([f for f in all_files if f.is_file()])
        
        # Calculate total size
        total_size = sum(f.stat().st_size for f in all_files if f.is_file())
        
        manifest = {
            "production_environment_refined": {
                "path": str(self.production_path),
                "created_at": self.start_time.isoformat(),
                "completed_at": end_time.isoformat(),
                "build_duration_seconds": duration.total_seconds(),
                "builder_version": "refined_v1.0"
            },
            "environment_statistics": {
                "total_files": file_count,
                "total_size_mb": round(total_size / (1024*1024), 2),
                "essential_files_only": True,
                "documentation_in_database": True
            },
            "validation_results": {
                "overall_score": score,
                "production_ready": production_ready,
                "error_count": validation["error_count"],
                "criteria_passed": validation,
                "validation_timestamp": end_time.isoformat()
            },
            "capabilities": {
                "github_copilot_integration": validation["github_copilot_ready"],
                "web_portal_interface": validation["web_templates_present"],
                "database_driven": validation["database_present"],
                "autonomous_operation": production_ready
            }
        }
        
        # Save manifest
        manifest_file = self.production_path / "refined_production_manifest.json"
        with open(manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        print(f"\nFinal manifest saved: {manifest_file}")
        return manifest

def main():
    """Main execution"""
    
    builder = RefinedProductionBuilder()
    
    try:
        print("=" * 80)
        print("REFINED PRODUCTION ENVIRONMENT BUILDER")
        print("=" * 80)
        
        # Step 1: Get essential files list
        essential_files = builder.get_essential_files()
        
        # Step 2: Verify files exist
        existing_files, missing_files = builder.verify_essential_files_exist(essential_files)
        
        # Step 3: Create clean production environment
        copied_files, failed_files = builder.create_clean_production_environment(existing_files)
        
        # Step 4: Migrate documentation
        docs_migrated = builder.migrate_all_documentation_to_database()
        
        # Step 5: Validate environment
        validation, score, production_ready = builder.validate_production_environment()
        
        # Step 6: Generate manifest
        manifest = builder.generate_final_manifest(validation, score, production_ready)
        
        # Final summary
        print("=" * 80)
        print("REFINED PRODUCTION BUILD COMPLETE")
        print("=" * 80)
        
        if production_ready:
            print("SUCCESS: 100% error-free production environment ready!")
            print(f"Location: {builder.production_path}")
            print(f"Files: {copied_files} essential files only")
            print(f"Documentation: {docs_migrated} documents in database")
            print(f"Score: {score:.1f}%")
            print("Ready for autonomous GitHub Copilot Integration!")
            return 0
        else:
            print("PARTIAL SUCCESS: Production environment created but needs attention")
            print(f"Score: {score:.1f}%")
            print(f"Errors: {validation['error_count']}")
            print("Review validation details above")
            return 1
            
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
