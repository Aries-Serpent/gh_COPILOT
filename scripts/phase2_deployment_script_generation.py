#!/usr/bin/env python3
"""
Phase 2 Production Deployment: Database-Driven Script Generation
Enterprise script generation using the deployed regeneration engine
"""

import os
import sys
import json
import sqlite3
from datetime import datetime
from pathlib import Path

def main():
    print("[LAUNCH] PRODUCTION DEPLOYMENT PHASE 2: DATABASE-DRIVEN SCRIPT GENERATION")
    print("=" * 80)
    
    # Define production path
    production_path = Path("e:/_copilot_production-001")
    
    # Verify Phase 1 completion
    print(f"[SEARCH] VERIFYING PHASE 1 COMPLETION")
    print("-" * 35)
    
    required_components = [
        production_path / "scripts" / "script_regeneration_engine.py",
        production_path / "databases" / "production.db",
        production_path / "generated_scripts"
    ]
    
    for component in required_components:
        if component.exists():
            print(f"[SUCCESS] Verified: {component.name}")
        else:
            print(f"[ERROR] Missing: {component}")
            return False
    
    # Change to production directory
    print(f"\n[WRENCH] INITIALIZING SCRIPT REGENERATION ENGINE")
    print("-" * 45)
    
    original_cwd = os.getcwd()
    os.chdir(str(production_path))
    
    try:
        # Add production scripts to path
        sys.path.insert(0, str(production_path / "scripts"))
        
        # Import the regeneration engine
        from script_regeneration_engine import ScriptRegenerationEngine
        
        print(f"[SUCCESS] Script regeneration engine imported successfully")
        
        # Initialize engine with production database
        engine = ScriptRegenerationEngine(
            database_path="databases/production.db",
            output_directory="generated_scripts"
        )
        
        print(f"[SUCCESS] Engine initialized with production database")
        
        # Validate regeneration capability
        print(f"\n[SHIELD]  VALIDATING REGENERATION CAPABILITY")
        print("-" * 40)
        
        validation_results = engine.validate_regeneration_capability()
        
        print(f"Database connectivity: {'[SUCCESS] OK' if validation_results['database_connectivity'] else '[ERROR] FAILED'}")
        print(f"Template availability: {'[SUCCESS] OK' if validation_results['template_availability'] else '[ERROR] FAILED'}")
        print(f"Output directory: {'[SUCCESS] OK' if validation_results['output_directory'] else '[ERROR] FAILED'}")
        print(f"Script metadata: {validation_results['script_metadata_count']} scripts")
        print(f"Templates: {validation_results['template_count']} templates")
        print(f"Capability Score: {validation_results['capability_score']}%")
        
        if validation_results['capability_score'] < 70:
            print(f"[WARNING]  Capability score too low for production deployment")
            return False
        
        # Execute script regeneration for high-priority scripts
        print(f"\n[PROCESSING] EXECUTING HIGH-PRIORITY SCRIPT REGENERATION")
        print("-" * 50)
        
        # Regenerate priority 1 scripts first
        print(f"[?] Regenerating priority 1 (critical) scripts...")
        summary_p1 = engine.regenerate_all_scripts(priority_filter=1)
        
        print(f"[WRENCH] Regenerating priority 2 (important) scripts...")
        summary_p2 = engine.regenerate_all_scripts(priority_filter=2)
        
        # Database category scripts
        print(f"[FILE_CABINET]  Regenerating database category scripts...")
        summary_db = engine.regenerate_all_scripts(category_filter="database")
        
        # Combine summaries
        total_generated = (
            summary_p1.get('performance_metrics', {}).get('total_files_generated', 0) +
            summary_p2.get('performance_metrics', {}).get('total_files_generated', 0) +
            summary_db.get('performance_metrics', {}).get('total_files_generated', 0)
        )
        
        print(f"\n[BAR_CHART] SCRIPT GENERATION SUMMARY")
        print("-" * 30)
        print(f"Priority 1 scripts: {summary_p1.get('performance_metrics', {}).get('total_files_generated', 0)}")
        print(f"Priority 2 scripts: {summary_p2.get('performance_metrics', {}).get('total_files_generated', 0)}")
        print(f"Database scripts: {summary_db.get('performance_metrics', {}).get('total_files_generated', 0)}")
        print(f"Total generated: {total_generated}")
        
        # List generated scripts
        generated_scripts_dir = production_path / "generated_scripts"
        if generated_scripts_dir.exists():
            generated_files = list(generated_scripts_dir.rglob("*.py"))
            print(f"\n[?] GENERATED SCRIPTS ({len(generated_files)} files):")
            for script_file in generated_files[:10]:  # Show first 10
                relative_path = script_file.relative_to(production_path)
                print(f"  [SUCCESS] {relative_path}")
            
            if len(generated_files) > 10:
                print(f"  ... and {len(generated_files) - 10} more files")
        
        # Generate Phase 2 report
        print(f"\n[CLIPBOARD] GENERATING PHASE 2 DEPLOYMENT REPORT")
        print("-" * 42)
        
        phase2_report = {
            "deployment_id": f"PROD_DEPLOY_PHASE2_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "phase": 2,
            "phase_name": "Database-Driven Script Generation",
            "production_path": str(production_path),
            "status": "COMPLETED",
            "regeneration_capability": validation_results,
            "generation_summary": {
                "priority_1_scripts": summary_p1.get('performance_metrics', {}),
                "priority_2_scripts": summary_p2.get('performance_metrics', {}),
                "database_scripts": summary_db.get('performance_metrics', {}),
                "total_files_generated": total_generated
            },
            "generated_files_count": len(list(generated_scripts_dir.rglob("*.py"))) if generated_scripts_dir.exists() else 0,
            "validation_results": {
                "regeneration_engine_functional": validation_results['capability_score'] >= 70,
                "scripts_generated_successfully": total_generated > 0,
                "database_accessible": validation_results['database_connectivity'],
                "templates_available": validation_results['template_availability']
            },
            "next_phase": {
                "phase_number": 3,
                "phase_name": "Documentation Migration",
                "description": "Migrate all documentation to production database"
            }
        }
        
        # Save Phase 2 report
        report_file = production_path / "logs" / "phase_2_deployment_report.json"
        with open(report_file, 'w') as f:
            json.dump(phase2_report, f, indent=2, default=str)
        
        print(f"[SUCCESS] Phase 2 report saved: {report_file}")
        
        # Final summary
        print(f"\n[TARGET] PHASE 2 DEPLOYMENT SUMMARY")
        print("=" * 40)
        
        all_validations_passed = all(phase2_report['validation_results'].values())
        
        print(f"Status: {'[SUCCESS] COMPLETED' if all_validations_passed else '[WARNING] PARTIAL'}")
        print(f"Regeneration Capability: {validation_results['capability_score']}%")
        print(f"Scripts Generated: {total_generated}")
        print(f"Database Scripts: {phase2_report['generated_files_count']}")
        
        if all_validations_passed and total_generated > 0:
            print(f"\n[LAUNCH] READY FOR PHASE 3: DOCUMENTATION MIGRATION")
            return True
        else:
            print(f"\n[WARNING]  PHASE 2 ISSUES DETECTED - REVIEW REQUIRED")
            return False
            
    except Exception as e:
        print(f"[ERROR] Phase 2 execution failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        os.chdir(original_cwd)
        if str(production_path / "scripts") in sys.path:
            sys.path.remove(str(production_path / "scripts"))

if __name__ == "__main__":
    success = main()
    print(f"\nPhase 2 result: {'SUCCESS' if success else 'NEEDS ATTENTION'}")
    sys.exit(0 if success else 1)
