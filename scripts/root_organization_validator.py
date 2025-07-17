#!/usr/bin/env python3
"""
📁 Root Folder Organization Validator
====================================
Validate that only intended files remain in root folder
"""

import os
import json
from datetime import datetime
from pathlib import Path
import hashlib

def validate_root_organization():
    """📁 Validate root folder organization and file placement"""
    start_time = datetime.now()
    
    print("📁 ROOT FOLDER ORGANIZATION VALIDATOR")
    print("=" * 60)
    print(f"🕐 Validation Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📂 Root Directory: {os.getcwd()}")
    print("=" * 60)
    
    # Define intended files for root folder
    intended_root_files = {
        # Core project files
        'README.md': 'Main project documentation',
        'pyproject.toml': 'Python project configuration',
        'Makefile': 'Build automation',
        'docker-compose.yml': 'Docker orchestration',
        'Dockerfile': 'Container configuration',
        
        # Navigation and mission files
        'COPILOT_NAVIGATION_MAP.json': 'Project navigation map',
        'ENTERPRISE_DEVELOPMENT_MISSION_ACCOMPLISHED.md': 'Mission status',
        'FINAL_LESSONS_LEARNED_INTEGRATION_VALIDATION.md': 'Lessons learned',
        'UNIFIED_WRAP_UP_ORCHESTRATOR_IMPLEMENTATION_COMPLETE.md': 'Wrap-up status',
        
        # Temporary validation files (acceptable)
        'temp_db_check.py': 'Temporary database validation script'
    }
    
    # Define file patterns that should NOT be in root
    should_not_be_in_root = {
        '*.db': 'databases/',
        '*.sqlite': 'databases/',
        '*.log': 'logs/',
        '*.json': 'config/ (except COPILOT_NAVIGATION_MAP.json)',
        '*.csv': 'data/',
        '*.xlsx': 'data/',
        '*.py': 'scripts/ or appropriate module folder (except temp files)',
        '*.ps1': 'scripts/',
        '*.bat': 'scripts/',
        '*.sh': 'scripts/',
        '*.txt': 'docs/ or logs/',
        '*.backup': 'Should not exist (external backups only)',
        '*.bak': 'Should not exist (external backups only)'
    }
    
    # Scan root directory
    root_path = Path(".")
    actual_root_files = []
    misplaced_files = []
    correctly_placed_files = []
    
    print("\n📋 SCANNING ROOT DIRECTORY")
    print("-" * 40)
    
    for item in root_path.iterdir():
        if item.is_file():
            actual_root_files.append(item.name)
            
            # Check if file is intended for root
            if item.name in intended_root_files:
                correctly_placed_files.append({
                    'file': item.name,
                    'description': intended_root_files[item.name],
                    'size': item.stat().st_size,
                    'status': 'CORRECT'
                })
                print(f"✅ {item.name}: {intended_root_files[item.name]}")
            else:
                # Check if file should be moved elsewhere
                file_ext = item.suffix.lower()
                suggested_location = None
                
                if file_ext == '.db' or file_ext == '.sqlite':
                    suggested_location = 'databases/'
                elif file_ext == '.log':
                    suggested_location = 'logs/'
                elif file_ext == '.py' and 'temp' not in item.name:
                    suggested_location = 'scripts/ or appropriate module'
                elif file_ext == '.json' and item.name != 'COPILOT_NAVIGATION_MAP.json':
                    suggested_location = 'config/'
                elif file_ext in ['.csv', '.xlsx']:
                    suggested_location = 'data/'
                elif file_ext in ['.ps1', '.bat', '.sh']:
                    suggested_location = 'scripts/'
                elif file_ext == '.txt':
                    suggested_location = 'docs/ or logs/'
                elif 'backup' in item.name.lower() or item.suffix == '.bak':
                    suggested_location = 'EXTERNAL BACKUP ONLY'
                
                if suggested_location:
                    misplaced_files.append({
                        'file': item.name,
                        'size': item.stat().st_size,
                        'suggested_location': suggested_location,
                        'status': 'MISPLACED'
                    })
                    print(f"⚠️  {item.name}: Should be in {suggested_location}")
                else:
                    # Unknown file type - mark for review
                    misplaced_files.append({
                        'file': item.name,
                        'size': item.stat().st_size,
                        'suggested_location': 'REVIEW NEEDED',
                        'status': 'UNKNOWN'
                    })
                    print(f"❓ {item.name}: Unknown file type - review needed")
    
    # Check for missing intended files
    missing_files = []
    for intended_file in intended_root_files:
        if intended_file not in actual_root_files:
            missing_files.append({
                'file': intended_file,
                'description': intended_root_files[intended_file],
                'status': 'MISSING'
            })
    
    print(f"\n📊 ROOT FOLDER ANALYSIS RESULTS")
    print("-" * 40)
    print(f"📁 Total files in root: {len(actual_root_files)}")
    print(f"✅ Correctly placed: {len(correctly_placed_files)}")
    print(f"⚠️  Misplaced files: {len(misplaced_files)}")
    print(f"❌ Missing intended files: {len(missing_files)}")
    
    # Detailed misplaced files report
    if misplaced_files:
        print(f"\n⚠️  MISPLACED FILES DETAILS")
        print("-" * 40)
        for file_info in misplaced_files:
            print(f"📄 {file_info['file']}")
            print(f"   Size: {file_info['size']} bytes")
            print(f"   Should be in: {file_info['suggested_location']}")
            print(f"   Status: {file_info['status']}")
            print()
    
    # Missing files report
    if missing_files:
        print(f"\n❌ MISSING INTENDED FILES")
        print("-" * 40)
        for file_info in missing_files:
            print(f"📄 {file_info['file']}: {file_info['description']}")
    
    # Directory structure validation
    print(f"\n📁 DIRECTORY STRUCTURE VALIDATION")
    print("-" * 40)
    
    expected_directories = [
        'scripts', 'databases', 'docs', 'logs', 'config',
        'copilot', 'web_gui', 'tests', 'reports', 'validation'
    ]
    
    missing_directories = []
    present_directories = []
    
    for dir_name in expected_directories:
        dir_path = Path(dir_name)
        if dir_path.exists() and dir_path.is_dir():
            file_count = len(list(dir_path.rglob("*")))
            present_directories.append({
                'directory': dir_name,
                'file_count': file_count,
                'status': 'PRESENT'
            })
            print(f"✅ {dir_name}/: {file_count} files")
        else:
            missing_directories.append({
                'directory': dir_name,
                'status': 'MISSING'
            })
            print(f"❌ {dir_name}/: Missing")
    
    # Calculate organization score
    total_intended = len(intended_root_files)
    correctly_placed_count = len(correctly_placed_files)
    misplaced_count = len(misplaced_files)
    
    if total_intended > 0:
        organization_score = (correctly_placed_count / (correctly_placed_count + misplaced_count)) * 100
    else:
        organization_score = 0
    
    # Overall assessment
    print(f"\n📈 ORGANIZATION ASSESSMENT")
    print("-" * 40)
    print(f"📊 Organization Score: {organization_score:.1f}%")
    
    if organization_score >= 95:
        assessment = "EXCELLENT"
        assessment_icon = "🏆"
    elif organization_score >= 85:
        assessment = "GOOD"
        assessment_icon = "✅"
    elif organization_score >= 70:
        assessment = "NEEDS_IMPROVEMENT"
        assessment_icon = "⚠️"
    else:
        assessment = "POOR"
        assessment_icon = "❌"
    
    print(f"{assessment_icon} Overall Assessment: {assessment}")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS")
    print("-" * 40)
    
    recommendations = []
    
    if misplaced_files:
        db_files = [f for f in misplaced_files if f['file'].endswith('.db')]
        if db_files:
            recommendations.append(f"🗄️ Move {len(db_files)} database file(s) to databases/ folder")
        
        script_files = [f for f in misplaced_files if f['file'].endswith('.py') and 'temp' not in f['file']]
        if script_files:
            recommendations.append(f"🐍 Move {len(script_files)} Python script(s) to scripts/ folder")
        
        config_files = [f for f in misplaced_files if f['file'].endswith('.json') and f['file'] != 'COPILOT_NAVIGATION_MAP.json']
        if config_files:
            recommendations.append(f"⚙️ Move {len(config_files)} configuration file(s) to config/ folder")
        
        log_files = [f for f in misplaced_files if f['file'].endswith('.log')]
        if log_files:
            recommendations.append(f"📋 Move {len(log_files)} log file(s) to logs/ folder")
    
    if missing_directories:
        recommendations.append(f"📁 Create missing directories: {', '.join([d['directory'] for d in missing_directories])}")
    
    if not recommendations:
        recommendations = [
            "🎯 Root folder organization is optimal",
            "✅ All files are correctly placed",
            "🏆 Maintain current organization standards"
        ]
    
    for rec in recommendations:
        print(f"{rec}")
    
    # Save validation report
    validation_report = {
        'validation_time': start_time.isoformat(),
        'root_directory': os.getcwd(),
        'total_root_files': len(actual_root_files),
        'correctly_placed_files': correctly_placed_files,
        'misplaced_files': misplaced_files,
        'missing_files': missing_files,
        'present_directories': present_directories,
        'missing_directories': missing_directories,
        'organization_score': organization_score,
        'assessment': assessment,
        'recommendations': recommendations
    }
    
    # Calculate duration
    duration = (datetime.now() - start_time).total_seconds()
    
    print(f"\n📁 ROOT ORGANIZATION VALIDATION COMPLETE")
    print("=" * 50)
    print(f"🕐 Duration: {duration:.2f} seconds")
    print(f"📊 Organization Score: {organization_score:.1f}%")
    print(f"{assessment_icon} Assessment: {assessment}")
    print(f"💡 Recommendations: {len(recommendations)}")
    
    # Save report
    report_file = f"validation/root_organization_validation_{start_time.strftime('%Y%m%d_%H%M%S')}.json"
    os.makedirs("validation", exist_ok=True)
    
    try:
        with open(report_file, 'w') as f:
            json.dump(validation_report, f, indent=2)
        print(f"📄 Report saved: {report_file}")
    except Exception as e:
        print(f"⚠️  Could not save report: {e}")
    
    return validation_report

if __name__ == "__main__":
    validate_root_organization()
