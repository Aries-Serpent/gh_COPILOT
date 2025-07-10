#!/usr/bin/env python3
"""
REFINED PRODUCTION ENVIRONMENT BUILDER
Creates 100% error-free minimal production environment with EXACT necessary file"s""
"""

import os
import sys
import json
import shutil
import sqlite3
import datetime
from pathlib import Path


class RefinedProductionBuilder:
  " "" """Creates minimal production environment with only essential operational fil"e""s"""

    def __init__(self):
        self.start_time = datetime.datetime.now()
        self.sandbox_path = Pat"h""("e:/gh_COPIL"O""T")
        self.production_path = Pat"h""("e:/_copilot_production-0"0""1")

        prin"t""("REFINED PRODUCTION BUILDER START"E""D")
        print"(""f"Start Time: {self.start_tim"e""}")
        print"(""f"Sandbox: {self.sandbox_pat"h""}")
        print"(""f"Production: {self.production_pat"h""}")

    def get_essential_files(self):
      " "" """Define EXACT list of essential files needed for production operati"o""n"""

        # CORE ESSENTIAL FILES - Minimal set for 100% operation
        essential_files = [
    # 1. DATABASE (critical
]
          " "" "production."d""b",

            # 2. CORE WEB SYSTEM (critical for GitHub Copilot Integration)
          " "" "web_portal_enterprise_system."p""y",
          " "" "start_web_portal."p""y",
          " "" "simple_web_gui_launcher."p""y",

            # 3. GITHUB COPILOT INTEGRATION (critical)
          " "" "copilot_cli_relay_api."p""y",
          " "" "enhanced_logging_web_gui."p""y",

            # 4. CONFIGURATION (critical)
          " "" "requirements.t"x""t",

            # 5. WEB TEMPLATES (required for web interface)
          " "" "templates/dashboard.ht"m""l",
          " "" "templates/database.ht"m""l",
          " "" "templates/deployment.ht"m""l",
          " "" "templates/migration.ht"m""l",
          " "" "templates/backup_restore.ht"m""l",

            # 6. STATIC ASSETS (required for web interface)
          " "" "static/css/style.c"s""s",
          " "" "static/js/portal."j""s",

            # 7. LAUNCH SCRIPTS (for system startup)
          " "" "launch_web_portal.p"s""1"
        ]

        print"(""f"Essential files defined: {len(essential_files")""}")
        return essential_files

    def verify_essential_files_exist(self, essential_files):
      " "" """Verify all essential files exist in sandbox before copyi"n""g"""

        prin"t""("Verifying essential files exist in sandbox."."".")

        existing_files = [
        missing_files = [
    for file_path in essential_files:
            full_path = self.sandbox_path / file_path
            if full_path.exists(
]:
                existing_files.append(file_path)
                print"(""f"  FOUND: {file_pat"h""}")
            else:
                missing_files.append(file_path)
                print"(""f"  MISSING: {file_pat"h""}")

        print"(""f"Essential files verificatio"n"":")
        print"(""f"  Found: {len(existing_files")""}")
        print"(""f"  Missing: {len(missing_files")""}")

        if missing_files:
            prin"t""("WARNING: Some essential files are missin"g""!")
            # Try to find alternatives
            self.find_alternative_files(missing_files)

        return existing_files, missing_files

    def find_alternative_files(self, missing_files):
      " "" """Find alternative files for missing essential fil"e""s"""

        prin"t""("Searching for alternative files."."".")

        alternatives = {
          " "" "copilot_cli_relay_api."p""y":" ""["*copilot*relay*."p""y"","" "*cli*relay*."p""y"],
          " "" "web_portal_enterprise_system."p""y":" ""["*web*portal*."p""y"","" "*portal*enterprise*."p""y"],
          " "" "start_web_portal."p""y":" ""["*start*web*."p""y"","" "*launch*portal*."p""y"],
          " "" "enhanced_logging_web_gui."p""y":" ""["*logging*web*."p""y"","" "*web*gui*."p""y"]
        }

        for missing_file in missing_files:
            if missing_file in alternatives:
                print"(""f"  Searching alternatives for {missing_file"}"":")
                for pattern in alternatives[missing_file]:
                    matches = list(self.sandbox_path.rglob(pattern))
                    if matches:
                        print(
                           " ""f"    Alternative found: {matches[0].relative_to(self.sandbox_path")""}")
                        break

    def create_clean_production_environment(self, essential_files):
      " "" """Create completely clean production environment with only essential fil"e""s"""

        prin"t""("Creating clean production environment."."".")

        # Remove existing production directory completely
        if self.production_path.exists():
            prin"t""("Removing existing production directory."."".")
            shutil.rmtree(self.production_path)

        # Create fresh production directory
        self.production_path.mkdir(parents=True, exist_ok=True)
        print"(""f"Created fresh production directory: {self.production_pat"h""}")

        # Copy only essential files
        copied_files = 0
        failed_files = [
    prin"t""("Copying essential files.".""."
]

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
                    print"(""f"  COPIED: {file_pat"h""}")

                except Exception as e:
                    failed_files.append"(""f"{file_path}: {"e""}")
                    print"(""f"  FAILED: {file_path} - {"e""}")
            else:
                failed_files.append"(""f"{file_path}: Not fou"n""d")
                print"(""f"  NOT FOUND: {file_pat"h""}")

        print"(""f"File copying complet"e"":")
        print"(""f"  Successfully copied: {copied_file"s""}")
        print"(""f"  Failed: {len(failed_files")""}")

        return copied_files, failed_files

    def migrate_all_documentation_to_database(self):
      " "" """Migrate ALL documentation from filesystem to databa"s""e"""

        prin"t""("Migrating documentation to database."."".")

        # Connect to production database
        db_path = self.production_path "/"" "production."d""b"

        if not db_path.exists():
            # Copy database from sandbox
            sandbox_db = self.sandbox_path "/"" "production."d""b"
            if sandbox_db.exists():
                shutil.copy2(sandbox_db, db_path)
                print"(""f"Database copied to production: {db_pat"h""}")
            else:
                prin"t""("ERROR: production.db not found in sandbo"x""!")
                return 0

        # Open database and create documentation table
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            # Create comprehensive documentation table
            cursor.execute(
                )
          " "" """)

            # Migrate ALL documentation files from sandbox
            doc_patterns = [
            ]

            total_docs = 0
            total_size = 0

            for pattern in doc_patterns:
                for doc_file in self.sandbox_path.rglob(pattern):
                    if doc_file.is_file():
                        try:
                            content = doc_file.read_text(]
                                encodin"g""='utf'-''8', error's''='igno'r''e')
                            relative_path = doc_file.relative_to(]
                                self.sandbox_path)
                            file_size = doc_file.stat().st_size

                            # Insert into database
                            cursor.execute(
                                (doc_category, doc_title, doc_content,
                                 original_path, file_size)
                                VALUES (?, ?, ?, ?, ?)
                          ' '' """, (]
                                self._categorize_document(doc_file),
                                doc_file.name,
                                content,
                                str(relative_path),
                                file_size
                            ))

                            total_docs += 1
                            total_size += file_size

                            if total_docs % 100 == 0:
                                print"(""f"  Migrated {total_docs} documents."."".")

                        except Exception as e:
                            print(
                               " ""f"  WARNING: Could not migrate {doc_file}: {"e""}")

            conn.commit()

            # Verify migration
            cursor.execute(
              " "" "SELECT COUNT(*), SUM(file_size) FROM all_documentati"o""n")
            db_docs, db_size = cursor.fetchone()

            print"(""f"Documentation migration complet"e"":")
            print"(""f"  Documents migrated: {total_doc"s""}")
            print"(""f"  Total size: {total_size / (1024*1024):.1f} "M""B")
            print"(""f"  Documents in database: {db_doc"s""}")
            print"(""f"  Database size: {(db_size or 0) / (1024*1024):.1f} "M""B")

            return total_docs

    def _categorize_document(self, file_path):
      " "" """Categorize document ty"p""e"""
        name = file_path.name.lower()
        i"f"" "repo"r""t" in name:
            retur"n"" "repor"t""s"
        eli"f"" "summa"r""y" in name:
            retur"n"" "summari"e""s"
        eli"f"" "analys"i""s" in name:
            retur"n"" "analys"i""s"
        eli"f"" "resul"t""s" in name:
            retur"n"" "resul"t""s"
        eli"f"" "read"m""e" in name:
            retur"n"" "read"m""e"
        elif file_path.suffix ="="" "."m""d":
            retur"n"" "markdo"w""n"
        else:
            retur"n"" "documentati"o""n"

    def validate_production_environment(self):
      " "" """Comprehensive validation of production environme"n""t"""

        prin"t""("Validating production environment."."".")

        validation = {
          " "" "validation_detai"l""s": []
        }

        # 1. Database validation
        db_path = self.production_path "/"" "production."d""b"
        if db_path.exists():
            try:
                with sqlite3.connect(db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                      " "" "SELECT COUNT(*) FROM sqlite_master WHERE typ"e""='tab'l''e'")
                    table_count = cursor.fetchone()[0]

                    validatio"n""["database_prese"n""t"] = table_count >= 5
                    validatio"n""["validation_detai"l""s"].append(]
                       " ""f"Database tables: {table_coun"t""}")

                    # Check documentation table
                    cursor.execut"e""("SELECT COUNT(*) FROM all_documentati"o""n")
                    doc_count = cursor.fetchone()[0]
                    validatio"n""["validation_detai"l""s"].append(]
                       " ""f"Documents in database: {doc_coun"t""}")

            except Exception as e:
                validatio"n""["error_cou"n""t"] += 1
                validatio"n""["validation_detai"l""s"].append"(""f"Database error: {"e""}")

        # 2. Essential files validation
        essential_core = [
        ]

        present_count = 0
        for file_name in essential_core:
            if (self.production_path / file_name).exists():
                present_count += 1
                validatio"n""["validation_detai"l""s"].append(]
                   " ""f"Essential file present: {file_nam"e""}")
            else:
                validatio"n""["validation_detai"l""s"].append(]
                   " ""f"Essential file MISSING: {file_nam"e""}")

        validatio"n""["essential_files_prese"n""t"] = present_count == len(]
            essential_core)

        # 3. No documentation files in filesystem
        doc_files = [
        for pattern in" ""["*."m""d"","" "*.t"x""t"","" "*_report"_""*"]:
            doc_files.extend(list(self.production_path.rglob(pattern)))

        validatio"n""["no_documentation_fil"e""s"] = len(doc_files) == 0
        validatio"n""["validation_detai"l""s"].append(]
           " ""f"Documentation files in filesystem: {len(doc_files")""}")

        # 4. Python syntax validation
        python_files = list(self.production_path.rglo"b""("*."p""y"))
        syntax_errors = 0

        for py_file in python_files:
            try:
                with open(py_file","" '''r', encodin'g''='utf'-''8') as f:
                    compile(f.read(), py_file','' 'ex'e''c')
            except SyntaxError as e:
                syntax_errors += 1
                validatio'n''["validation_detai"l""s"].append(]
                   " ""f"Syntax error in {py_file.name}: {"e""}")
            except Exception:
                pass

        validatio"n""["python_syntax_val"i""d"] = syntax_errors == 0
        validatio"n""["error_cou"n""t"] += syntax_errors
        validatio"n""["validation_detai"l""s"].append(]
           " ""f"Python files: {len(python_files)}, Syntax errors: {syntax_error"s""}")

        # 5. GitHub Copilot Integration readiness
        copilot_files = [
        ]

        copilot_present = 0
        for file_name in copilot_files:
            if (self.production_path / file_name).exists():
                copilot_present += 1

        validatio"n""["github_copilot_rea"d""y"] = copilot_present >= 1
        validatio"n""["validation_detai"l""s"].append(]
           " ""f"GitHub Copilot files present: {copilot_present}/{len(copilot_files")""}")

        # 6. Web templates validation
        template_files = list(self.production_path.glo"b""("templates/*.ht"m""l"))
        validatio"n""["web_templates_prese"n""t"] = len(template_files) >= 3
        validatio"n""["validation_detai"l""s"].append(]
           " ""f"Web templates: {len(template_files")""}")

        # 7. Static assets validation
        css_files = list(self.production_path.glo"b""("static/css/*.c"s""s"))
        js_files = list(self.production_path.glo"b""("static/js/*."j""s"))
        validatio"n""["static_assets_prese"n""t"] = len(]
            css_files) >= 1 and len(js_files) >= 1
        validatio"n""["validation_detai"l""s"].append(]
           " ""f"Static assets: {len(css_files)} CSS, {len(js_files)} "J""S")

        # Calculate overall score
        criteria = [
        ]

        passed = sum(1 for criterion in criteria if validation[criterion])
        score = (passed / len(criteria)) * 100

        production_ready = (score >= 100 and validatio"n""["error_cou"n""t"] == 0)

        prin"t""("VALIDATION RESULT"S"":")
        print(
           " ""f"  Score: {score:.1f}% ({passed}/{len(criteria)} criteria passe"d"")")
        print"(""f"  Errors: {validatio"n""['error_cou'n''t'']''}")
        print"(""f"  Production Ready: {production_read"y""}")

        prin"t""("\nValidation Detail"s"":")
        for detail in validatio"n""["validation_detai"l""s"]:
            print"(""f"  - {detai"l""}")

        return validation, score, production_ready

    def generate_final_manifest(self, validation, score, production_ready):
      " "" """Generate final production manife"s""t"""

        end_time = datetime.datetime.now()
        duration = end_time - self.start_time

        # Count files in production
        all_files = list(self.production_path.rglo"b""("""*"))
        file_count = len([f for f in all_files if f.is_file()])

        # Calculate total size
        total_size = sum(f.stat().st_size for f in all_files if f.is_file())

        manifest = {
              " "" "pa"t""h": str(self.production_path),
              " "" "created_"a""t": self.start_time.isoformat(),
              " "" "completed_"a""t": end_time.isoformat(),
              " "" "build_duration_secon"d""s": duration.total_seconds(),
              " "" "builder_versi"o""n"":"" "refined_v1".""0"
            },
          " "" "environment_statisti"c""s": {]
              " "" "total_size_"m""b": round(total_size / (1024*1024), 2),
              " "" "essential_files_on"l""y": True,
              " "" "documentation_in_databa"s""e": True
            },
          " "" "validation_resul"t""s": {]
              " "" "error_cou"n""t": validatio"n""["error_cou"n""t"],
              " "" "criteria_pass"e""d": validation,
              " "" "validation_timesta"m""p": end_time.isoformat()
            },
          " "" "capabiliti"e""s": {]
              " "" "github_copilot_integrati"o""n": validatio"n""["github_copilot_rea"d""y"],
              " "" "web_portal_interfa"c""e": validatio"n""["web_templates_prese"n""t"],
              " "" "database_driv"e""n": validatio"n""["database_prese"n""t"],
              " "" "autonomous_operati"o""n": production_ready
            }
        }

        # Save manifest
        manifest_file = self.production_path "/"" "refined_production_manifest.js"o""n"
        with open(manifest_file","" '''w') as f:
            json.dump(manifest, f, indent=2)

        print'(''f"\nFinal manifest saved: {manifest_fil"e""}")
        return manifest


def main():
  " "" """Main executi"o""n"""

    builder = RefinedProductionBuilder()

    try:
        prin"t""("""=" * 80)
        prin"t""("REFINED PRODUCTION ENVIRONMENT BUILD"E""R")
        prin"t""("""=" * 80)

        # Step 1: Get essential files list
        essential_files = builder.get_essential_files()

        # Step 2: Verify files exist
        existing_files, missing_files = builder.verify_essential_files_exist(]
            essential_files)

        # Step 3: Create clean production environment
        copied_files, failed_files = builder.create_clean_production_environment(]
            existing_files)

        # Step 4: Migrate documentation
        docs_migrated = builder.migrate_all_documentation_to_database()

        # Step 5: Validate environment
        validation, score, production_ready = builder.validate_production_environment()

        # Step 6: Generate manifest
        manifest = builder.generate_final_manifest(]
            validation, score, production_ready)

        # Final summary
        prin"t""("""=" * 80)
        prin"t""("REFINED PRODUCTION BUILD COMPLE"T""E")
        prin"t""("""=" * 80)

        if production_ready:
            prin"t""("SUCCESS: 100% error-free production environment read"y""!")
            print"(""f"Location: {builder.production_pat"h""}")
            print"(""f"Files: {copied_files} essential files on"l""y")
            print"(""f"Documentation: {docs_migrated} documents in databa"s""e")
            print"(""f"Score: {score:.1f"}""%")
            prin"t""("Ready for autonomous GitHub Copilot Integratio"n""!")
            return 0
        else:
            prin"t""("PARTIAL SUCCESS: Production environment created but needs attenti"o""n")
            print"(""f"Score: {score:.1f"}""%")
            print"(""f"Errors: {validatio"n""['error_cou'n''t'']''}")
            prin"t""("Review validation details abo"v""e")
            return 1

    except Exception as e:
        print"(""f"CRITICAL ERROR: {"e""}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ ="="" "__main"_""_":
    sys.exit(main())"
""