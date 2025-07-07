#!/usr/bin/env python3
"""
[SEARCH] DISASTER RECOVERY FACTOR ANALYSIS
===================================

DUAL COPILOT: [SUCCESS] ACTIVE | Anti-Recursion: [SUCCESS] PROTECTED | Visual: [TARGET] INDICATORS
DATABASE-FIRST: Analyzing recovery capability factors for 90-100% target

MISSION: Understand why recovery is only 35% and create enhancement strategy
"""

import sqlite3
import os
import json
from datetime import datetime
from pathlib import Path

def analyze_recovery_factors():
    """Comprehensive analysis of disaster recovery factors"""
    print("[SEARCH] DISASTER RECOVERY FACTOR ANALYSIS")
    print("=" * 50)
    
    # Define recovery factors with weights (must total 100%)
    recovery_factors = {
        'script_regeneration': {
            'weight': 40, 
            'status': False, 
            'details': [],
            'description': 'Ability to regenerate code from database templates'
        },
        'template_recovery': {
            'weight': 25, 
            'status': False, 
            'details': [],
            'description': 'Template Intelligence Platform data preservation'
        },
        'configuration_recovery': {
            'weight': 15, 
            'status': False, 
            'details': [],
            'description': 'System configuration and settings restoration'
        },
        'database_schema_recovery': {
            'weight': 10, 
            'status': False, 
            'details': [],
            'description': 'Database structure and relationship recovery'
        },
        'enterprise_deployment_recovery': {
            'weight': 10, 
            'status': False, 
            'details': [],
            'description': 'Enterprise deployment configurations and workflows'
        }
    }
    
    # Analyze production.db
    if os.path.exists('production.db'):
        print("[BAR_CHART] ANALYZING production.db...")
        conn = sqlite3.connect('production.db')
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"  Tables found: {len(tables)}")
        
        for table in sorted(tables):
            print(f"    - {table}")
        
        # Check script regeneration capability
        if 'tracked_scripts' in tables:
            cursor.execute('SELECT COUNT(*) FROM tracked_scripts')
            script_count = cursor.fetchone()[0]
            print(f"  [NOTES] Tracked scripts: {script_count}")
            recovery_factors['script_regeneration']['status'] = script_count > 1000
            recovery_factors['script_regeneration']['details'].append(f'{script_count} scripts tracked')
            
            # Get script categories
            try:
                cursor.execute("SELECT DISTINCT category FROM tracked_scripts WHERE category IS NOT NULL")
                categories = [row[0] for row in cursor.fetchall()]
                recovery_factors['script_regeneration']['details'].extend([f'Category: {cat}' for cat in categories])
            except:
                pass
        
        # Check template recovery
        template_tables = [t for t in tables if 'template' in t.lower()]
        if template_tables:
            recovery_factors['template_recovery']['status'] = True
            recovery_factors['template_recovery']['details'].extend(template_tables)
            print(f"  [CLIPBOARD] Template tables: {template_tables}")
            
            # Check template data
            for table in template_tables:
                try:
                    cursor.execute(f'SELECT COUNT(*) FROM {table}')
                    count = cursor.fetchone()[0]
                    recovery_factors['template_recovery']['details'].append(f'{table}: {count} entries')
                except:
                    pass
        
        # Check configuration recovery
        config_tables = [t for t in tables if 'config' in t.lower() or 'setting' in t.lower()]
        if config_tables:
            recovery_factors['configuration_recovery']['status'] = True
            recovery_factors['configuration_recovery']['details'].extend(config_tables)
            print(f"  [GEAR] Config tables: {config_tables}")
        
        # Check database schema recovery
        schema_tables = [t for t in tables if any(word in t.lower() for word in ['schema', 'structure', 'metadata'])]
        if schema_tables or len(tables) > 10:  # If we have many tables, schema recovery is possible
            recovery_factors['database_schema_recovery']['status'] = len(tables) > 10
            recovery_factors['database_schema_recovery']['details'].append(f'{len(tables)} tables for schema reference')
        
        # Check enterprise deployment recovery
        platform_tables = [t for t in tables if any(word in t.lower() for word in ['platform', 'deployment', 'enterprise'])]
        if platform_tables:
            recovery_factors['enterprise_deployment_recovery']['status'] = True
            recovery_factors['enterprise_deployment_recovery']['details'].extend(platform_tables)
            print(f"  [LAUNCH] Platform tables: {platform_tables}")
        
        conn.close()
    else:
        print("[ERROR] production.db not found!")
    
    # Check additional databases
    db_path = Path('databases')
    if db_path.exists():
        print(f"\n[BAR_CHART] ANALYZING databases folder...")
        db_files = list(db_path.glob('*.db'))
        print(f"  Additional databases: {len(db_files)}")
        for db_file in db_files:
            print(f"    - {db_file.name} ({db_file.stat().st_size} bytes)")
    
    # Calculate current score
    current_score = 0
    max_score = 0
    
    print("\n[CHART_INCREASING] RECOVERY FACTOR BREAKDOWN:")
    print("=" * 50)
    
    for factor, data in recovery_factors.items():
        max_score += data['weight']
        if data['status']:
            current_score += data['weight']
        
        status_icon = '[SUCCESS]' if data['status'] else '[ERROR]'
        print(f"{status_icon} {factor.upper()}: {data['weight']}% weight - {'AVAILABLE' if data['status'] else 'MISSING'}")
        print(f"    Description: {data['description']}")
        
        if data['details']:
            for detail in data['details']:
                print(f"    [?] {detail}")
        print()
    
    current_percentage = (current_score / max_score) * 100 if max_score > 0 else 0
    print(f"[TARGET] CURRENT RECOVERY SCORE: {current_percentage:.1f}% ({current_score}/{max_score})")
    
    # Identify what's needed for 90-100%
    print("\n[LAUNCH] PATH TO 90-100% RECOVERY CAPABILITY:")
    print("=" * 50)
    
    missing_capabilities = []
    for factor, data in recovery_factors.items():
        if not data['status']:
            missing_capabilities.append({
                'factor': factor,
                'weight': data['weight'],
                'description': data['description']
            })
    
    return recovery_factors, current_percentage, missing_capabilities

if __name__ == "__main__":
    factors, score, missing = analyze_recovery_factors()
    
    # Save analysis results
    analysis_results = {
        "timestamp": datetime.now().isoformat(),
        "current_score": score,
        "recovery_factors": factors,
        "missing_capabilities": missing,
        "enhancement_needed": 100 - score
    }
    
    with open('DISASTER_RECOVERY_ANALYSIS.json', 'w') as f:
        json.dump(analysis_results, f, indent=2)
    
    print(f"\n[SUCCESS] Analysis saved to DISASTER_RECOVERY_ANALYSIS.json")
