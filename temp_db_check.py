#!/usr/bin/env python3
"""
Database Structure Analysis for PIS Development
"""
import sqlite3
from pathlib import Path

def analyze_production_db():
    """Analyze production database structure"""
    db_path = Path("databases/production.db")
    
    if not db_path.exists():
        print("❌ databases/production.db not found")
        return
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Get tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"📊 Found {len(tables)} tables in production.db")
        
        if tables:
            for table in tables[:10]:  # Show first 10 tables
                print(f"  - {table[0]}")
                
                # Get row count for key tables
                if table[0] in ['enhanced_script_tracking', 'code_templates', 'file_system_mapping']:
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
                        count = cursor.fetchone()[0]
                        print(f"    → {count} records")
                    except Exception as e:
                        print(f"    → Error: {e}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

if __name__ == "__main__":
    analyze_production_db()
