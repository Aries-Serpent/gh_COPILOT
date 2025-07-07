#!/usr/bin/env python3
"""
Phase 1 Production Deployment: Script Regeneration Engine Validation
Simplified deployment with direct execution and visual indicators
"""

import os
import sys
import json
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path

def main():
    print("[LAUNCH] PRODUCTION DEPLOYMENT PHASE 1: SCRIPT REGENERATION ENGINE VALIDATION")
    print("=" * 80)
    
    # Define paths
    sandbox_path = Path("e:/gh_COPILOT")
    production_path = Path("e:/_copilot_production-001")
    
    print(f"[FOLDER] Sandbox: {sandbox_path}")
    print(f"[?] Production: {production_path}")
    
    # Phase 1: Create directory structure
    print(f"\n[WRENCH] CREATING PRODUCTION DIRECTORY STRUCTURE")
    print("-" * 50)
    
    directories = [
        production_path,
        production_path / "databases",
        production_path / "scripts", 
        production_path / "generated_scripts",
        production_path / "documentation",
        production_path / "configurations",
        production_path / "logs",
        production_path / "monitoring"
    ]
    
    for directory in directories:
        try:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"[SUCCESS] Created: {directory}")
        except Exception as e:
            print(f"[ERROR] Failed to create {directory}: {e}")
            return False
    
    # Phase 2: Copy critical files
    print(f"\n[?] COPYING CRITICAL FILES")
    print("-" * 30)
    
    # Copy script regeneration engine
    try:
        source_script = sandbox_path / "script_regeneration_engine.py"
        target_script = production_path / "scripts" / "script_regeneration_engine.py"
        
        if source_script.exists():
            shutil.copy2(source_script, target_script)
            print(f"[SUCCESS] Copied script regeneration engine: {target_script}")
        else:
            print(f"[WARNING]  Script regeneration engine not found: {source_script}")
    except Exception as e:
        print(f"[ERROR] Failed to copy script: {e}")
    
    # Copy production database
    try:
        source_db = sandbox_path / "production.db"
        target_db = production_path / "databases" / "production.db"
        
        if source_db.exists():
            shutil.copy2(source_db, target_db)
            print(f"[SUCCESS] Copied production database: {target_db}")
            
            # Verify database integrity
            try:
                conn = sqlite3.connect(target_db)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM enhanced_script_tracking")
                script_count = cursor.fetchone()[0]
                conn.close()
                print(f"[SUCCESS] Database verification: {script_count} scripts tracked")
            except Exception as e:
                print(f"[WARNING]  Database verification failed: {e}")
                
        else:
            print(f"[WARNING]  Production database not found: {source_db}")
    except Exception as e:
        print(f"[ERROR] Failed to copy database: {e}")
    
    # Phase 3: Test script regeneration capability
    print(f"\n[SHIELD]  VALIDATING SCRIPT REGENERATION CAPABILITY")
    print("-" * 45)
    
    try:
        # Change to production directory for testing
        original_cwd = os.getcwd()
        os.chdir(str(production_path))
        
        # Test if script regeneration engine can be imported and executed
        sys.path.insert(0, str(production_path / "scripts"))
        
        # Simple validation test
        regeneration_script = production_path / "scripts" / "script_regeneration_engine.py"
        if regeneration_script.exists():
            print(f"[SUCCESS] Script regeneration engine available")
            
            # Test basic syntax
            with open(regeneration_script, 'r') as f:
                content = f.read()
                
            import ast
            try:
                ast.parse(content)
                print(f"[SUCCESS] Script syntax validation: PASSED")
            except SyntaxError as e:
                print(f"[ERROR] Script syntax validation: FAILED - {e}")
                
        database_file = production_path / "databases" / "production.db"
        if database_file.exists():
            print(f"[SUCCESS] Production database accessible")
        else:
            print(f"[ERROR] Production database not accessible")
            
    except Exception as e:
        print(f"[ERROR] Validation failed: {e}")
    finally:
        os.chdir(original_cwd)
        if str(production_path / "scripts") in sys.path:
            sys.path.remove(str(production_path / "scripts"))
    
    # Phase 4: Generate deployment report
    print(f"\n[BAR_CHART] GENERATING PHASE 1 DEPLOYMENT REPORT")
    print("-" * 40)
    
    deployment_report = {
        "deployment_id": f"PROD_DEPLOY_PHASE1_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "timestamp": datetime.now().isoformat(),
        "phase": 1,
        "phase_name": "Script Regeneration Engine Validation",
        "production_path": str(production_path),
        "sandbox_path": str(sandbox_path),
        "status": "COMPLETED",
        "directories_created": [str(d.relative_to(production_path)) for d in directories[1:]],
        "files_deployed": [
            "scripts/script_regeneration_engine.py",
            "databases/production.db"
        ],
        "validation_results": {
            "script_engine_available": (production_path / "scripts" / "script_regeneration_engine.py").exists(),
            "database_available": (production_path / "databases" / "production.db").exists(),
            "directory_structure_complete": all(d.exists() for d in directories)
        },
        "next_phase": {
            "phase_number": 2,
            "phase_name": "Database-Driven Script Generation",
            "description": "Generate production scripts using the regeneration engine"
        }
    }
    
    # Save deployment report
    report_file = production_path / "logs" / "phase_1_deployment_report.json"
    with open(report_file, 'w') as f:
        json.dump(deployment_report, f, indent=2, default=str)
    
    print(f"[SUCCESS] Deployment report saved: {report_file}")
    
    # Final summary
    print(f"\n[TARGET] PHASE 1 DEPLOYMENT SUMMARY")
    print("=" * 40)
    print(f"Status: {'[SUCCESS] COMPLETED' if deployment_report['validation_results']['directory_structure_complete'] else '[WARNING] PARTIAL'}")
    print(f"Production Directory: {production_path}")
    print(f"Script Engine: {'[SUCCESS] DEPLOYED' if deployment_report['validation_results']['script_engine_available'] else '[ERROR] MISSING'}")
    print(f"Database: {'[SUCCESS] DEPLOYED' if deployment_report['validation_results']['database_available'] else '[ERROR] MISSING'}")
    
    all_validations_passed = all(deployment_report['validation_results'].values())
    
    if all_validations_passed:
        print(f"\n[LAUNCH] READY FOR PHASE 2: DATABASE-DRIVEN SCRIPT GENERATION")
        return True
    else:
        print(f"\n[WARNING]  PHASE 1 ISSUES DETECTED - REVIEW REQUIRED")
        return False

if __name__ == "__main__":
    success = main()
    print(f"\nDeployment result: {'SUCCESS' if success else 'NEEDS ATTENTION'}")
    sys.exit(0 if success else 1)
