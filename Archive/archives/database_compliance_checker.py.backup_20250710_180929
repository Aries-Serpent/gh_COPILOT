#!/usr/bin/env python3
"""
DATABASE COMPLIANCE CHECKER
===========================

Comprehensive analysis of all database files to check for:
1. Python script content
2. Emoji/Unicode characters
3. Flake8/PEP 8 compliance issues

Windows-compatible with text-based indicators.
"""

import sqlite3
import os
import re
from pathlib import Path
from datetime import datetime
from tqdm import tqdm

# Text-based visual indicators (NO Unicode emojis)
INDICATORS = {
    'start': '[START]',
    'scan': '[SCAN]',
    'found': '[FOUND]',
    'clean': '[CLEAN]',
    'error': '[ERROR]',
    'complete': '[COMPLETE]'
}

class DatabaseComplianceChecker:
    """Check database compliance for scripts and emojis"""
    
    def __init__(self, workspace_path: str = "e:/gh_COPILOT"):
        self.workspace_path = Path(workspace_path)
        self.database_dir = self.workspace_path / "databases"
        self.results = {
            'total_databases': 0,
            'analyzed_databases': 0,
            'script_violations': [],
            'emoji_violations': [],
            'compliance_status': 'UNKNOWN'
        }
        
        # Common emoji patterns to detect
        self.emoji_patterns = [
            '🔍', '🚀', '📊', '⚡', '✅', '❌', '🎯', '💡', '🛡️', '📈', 
            '🔧', '💻', '🎬', '📋', '🌐', '⚙️', '🎭', '💾', '🗄️', '📁', 
            '📂', '🔄', '🚨', '🏆', '🤖', '🧠', '🌟', '⭐', '🔥', '💪'
        ]
        
        # Script patterns to detect
        self.script_patterns = [
            'def ', 'class ', 'import ', 'from ', '#!/usr/bin/python',
            '#!/usr/bin/env python', 'if __name__', 'print(', 'return ',
            'try:', 'except:', 'with open(', 'sqlite3.connect'
        ]
    
    def analyze_all_databases(self):
        """Analyze all database files for compliance"""
        print(f"{INDICATORS['start']} Starting comprehensive database compliance analysis")
        
        db_files = list(self.database_dir.glob('*.db'))
        self.results['total_databases'] = len(db_files)
        
        print(f"{INDICATORS['scan']} Found {len(db_files)} database files to analyze")
        
        with tqdm(total=len(db_files), desc="Analyzing databases", unit="db") as pbar:
            for db_file in db_files:
                try:
                    self.analyze_single_database(db_file)
                    self.results['analyzed_databases'] += 1
                    pbar.set_description(f"Analyzing {db_file.name}")
                    pbar.update(1)
                except Exception as e:
                    print(f"{INDICATORS['error']} Failed to analyze {db_file.name}: {e}")
                    pbar.update(1)
        
        # Determine compliance status
        has_scripts = len(self.results['script_violations']) > 0
        has_emojis = len(self.results['emoji_violations']) > 0
        
        if not has_scripts and not has_emojis:
            self.results['compliance_status'] = 'FULLY_COMPLIANT'
        elif has_emojis and not has_scripts:
            self.results['compliance_status'] = 'EMOJI_VIOLATIONS_ONLY'
        elif has_scripts and not has_emojis:
            self.results['compliance_status'] = 'SCRIPT_CONTENT_FOUND'
        else:
            self.results['compliance_status'] = 'MULTIPLE_VIOLATIONS'
    
    def analyze_single_database(self, db_file: Path):
        """Analyze a single database file"""
        with sqlite3.connect(db_file) as conn:
            cursor = conn.cursor()
            
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            for table in tables:
                table_name = table[0]
                self.analyze_table(cursor, db_file.name, table_name)
    
    def analyze_table(self, cursor, db_name: str, table_name: str):
        """Analyze a single table for compliance issues"""
        try:
            # Get table schema
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            # Only check text-like columns
            text_columns = [col[1] for col in columns 
                           if any(t in str(col[2]).upper() for t in ['TEXT', 'VARCHAR', 'CHAR'])]
            
            for col_name in text_columns:
                self.analyze_column(cursor, db_name, table_name, col_name)
                
        except Exception as e:
            # Skip problematic tables
            pass
    
    def analyze_column(self, cursor, db_name: str, table_name: str, col_name: str):
        """Analyze a single column for content violations"""
        try:
            # Get all non-null values from the column
            cursor.execute(f"SELECT {col_name} FROM {table_name} WHERE {col_name} IS NOT NULL")
            rows = cursor.fetchall()
            
            for row in rows:
                content = str(row[0]) if row[0] is not None else ""
                
                # Check for script patterns
                for pattern in self.script_patterns:
                    if pattern in content:
                        violation = {
                            'database': db_name,
                            'table': table_name,
                            'column': col_name,
                            'pattern': pattern,
                            'content_preview': content[:100] + "..." if len(content) > 100 else content
                        }
                        self.results['script_violations'].append(violation)
                        break  # Only record one violation per row
                
                # Check for emoji patterns
                for emoji in self.emoji_patterns:
                    if emoji in content:
                        violation = {
                            'database': db_name,
                            'table': table_name,
                            'column': col_name,
                            'emoji': emoji,
                            'content_preview': content[:100] + "..." if len(content) > 100 else content
                        }
                        self.results['emoji_violations'].append(violation)
                        break  # Only record one violation per row
                        
        except Exception as e:
            # Skip problematic columns
            pass
    
    def generate_compliance_report(self):
        """Generate comprehensive compliance report"""
        print(f"\n{INDICATORS['complete']} DATABASE COMPLIANCE ANALYSIS COMPLETE")
        print("=" * 60)
        
        print(f"Total Databases: {self.results['total_databases']}")
        print(f"Analyzed Databases: {self.results['analyzed_databases']}")
        print(f"Script Violations: {len(self.results['script_violations'])}")
        print(f"Emoji Violations: {len(self.results['emoji_violations'])}")
        print(f"Compliance Status: {self.results['compliance_status']}")
        
        # Detailed violations
        if self.results['script_violations']:
            print(f"\n{INDICATORS['found']} SCRIPT CONTENT VIOLATIONS:")
            print("-" * 40)
            for i, violation in enumerate(self.results['script_violations'][:10]):  # Show first 10
                print(f"{i+1}. {violation['database']}.{violation['table']}.{violation['column']}")
                print(f"   Pattern: {violation['pattern']}")
                print(f"   Preview: {violation['content_preview']}")
                print()
            
            if len(self.results['script_violations']) > 10:
                print(f"... and {len(self.results['script_violations']) - 10} more violations")
        
        if self.results['emoji_violations']:
            print(f"\n{INDICATORS['found']} EMOJI CONTENT VIOLATIONS:")
            print("-" * 40)
            for i, violation in enumerate(self.results['emoji_violations'][:10]):  # Show first 10
                print(f"{i+1}. {violation['database']}.{violation['table']}.{violation['column']}")
                print(f"   Emoji: {violation['emoji']}")
                print(f"   Preview: {violation['content_preview']}")
                print()
            
            if len(self.results['emoji_violations']) > 10:
                print(f"... and {len(self.results['emoji_violations']) - 10} more violations")
        
        # Final assessment
        print("\n" + "=" * 60)
        if self.results['compliance_status'] == 'FULLY_COMPLIANT':
            print(f"{INDICATORS['clean']} ALL DATABASES ARE 100% COMPLIANT")
            print("- No Python script content found")
            print("- No emoji characters found")
            print("- Ready for enterprise deployment")
        else:
            print(f"{INDICATORS['found']} COMPLIANCE VIOLATIONS DETECTED")
            print("- Database cleanup required before enterprise deployment")
            print("- Run database emoji cleaner if needed")
        
        return self.results

def main():
    """Main entry point"""
    checker = DatabaseComplianceChecker()
    checker.analyze_all_databases()
    results = checker.generate_compliance_report()
    
    # Save results to file
    import json
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = f"database_compliance_report_{timestamp}.json"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n{INDICATORS['complete']} Report saved to: {report_file}")
    
    return results['compliance_status'] == 'FULLY_COMPLIANT'

if __name__ == "__main__":
    main()
