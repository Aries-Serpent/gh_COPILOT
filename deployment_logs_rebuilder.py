#!/usr/bin/env python3
"""
🔄 DEPLOYMENT LOGS DATABASE REBUILDER
================================================================
MISSION: Rebuild deployment_logs.db with only essential data
to achieve the 99.9MB target while maintaining functionality
================================================================
"""

import sqlite3
import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from tqdm import tqdm
import time

class DeploymentLogsRebuilder:
    """🔄 Clean Database Rebuilder for deployment_logs.db"""
    
    def __init__(self):
        self.start_time = datetime.now()
        workspace = Path(os.getenv("GH_COPILOT_WORKSPACE", "e:/gh_COPILOT"))
        self.old_db_path = workspace / "databases" / "deployment_logs.db"
        self.new_db_path = workspace / "databases" / "deployment_logs_optimized.db"
        self.backup_path = workspace / "databases" / "deployment_logs_backup.db"
        self.max_size_mb = 99.9
        self.max_size_bytes = int(self.max_size_mb * 1024 * 1024)
        
        print("="*80)
        print("🔄 DEPLOYMENT LOGS DATABASE REBUILDER")
        print(f"🚀 Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📁 Source: {self.old_db_path}")
        print(f"📁 Target: {self.new_db_path}")
        print(f"📏 Target Size: {self.max_size_mb} MB")
        print("="*80)
        
    def analyze_source_database(self):
        """🔍 Analyze source database structure and content"""
        analysis = {
            'tables': {},
            'total_rows': 0,
            'schema': {}
        }
        
        try:
            with sqlite3.connect(str(self.old_db_path)) as conn:
                cursor = conn.cursor()
                
                # Get all tables
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                
                for table_name, in tables:
                    if table_name.startswith('sqlite_'):
                        continue
                        
                    # Get table schema
                    cursor.execute(f"SELECT sql FROM sqlite_master WHERE name='{table_name}'")
                    schema = cursor.fetchone()
                    analysis['schema'][table_name] = schema[0] if schema else None
                    
                    # Get row count
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    row_count = cursor.fetchone()[0]
                    
                    # Get column info
                    cursor.execute(f"PRAGMA table_info({table_name})")
                    columns = cursor.fetchall()
                    
                    analysis['tables'][table_name] = {
                        'row_count': row_count,
                        'columns': [col[1] for col in columns],
                        'column_count': len(columns)
                    }
                    analysis['total_rows'] += row_count
                    
                print(f"📊 Analysis: {len(analysis['tables'])} tables, {analysis['total_rows']} total rows")
                
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            
        return analysis
        
    def create_optimized_database(self, analysis):
        """🏗️ Create optimized database with essential data only"""
        
        # Remove old optimized database if exists
        if self.new_db_path.exists():
            self.new_db_path.unlink()
            
        try:
            # Create new database
            with sqlite3.connect(str(self.new_db_path)) as new_conn:
                new_cursor = new_conn.cursor()
                
                # Connect to old database
                with sqlite3.connect(str(self.old_db_path)) as old_conn:
                    old_cursor = old_conn.cursor()
                    
                    # Set optimization pragmas for new database
                    new_cursor.execute('PRAGMA journal_mode=WAL')
                    new_cursor.execute('PRAGMA synchronous=NORMAL')
                    new_cursor.execute('PRAGMA cache_size=10000')
                    new_cursor.execute('PRAGMA page_size=4096')
                    
                    # Process each table
                    for table_name, table_info in analysis['tables'].items():
                        print(f"🔄 Processing table: {table_name} ({table_info['row_count']} rows)")
                        
                        # Create table schema
                        if table_name in analysis['schema'] and analysis['schema'][table_name]:
                            new_cursor.execute(analysis['schema'][table_name])
                        
                        # Determine how many rows to keep based on table type
                        if 'log' in table_name.lower():
                            # Keep only recent logs (last 7 days)
                            cutoff_date = datetime.now() - timedelta(days=7)
                            cutoff_timestamp = cutoff_date.isoformat()
                            
                            # Try to find timestamp column
                            timestamp_cols = ['timestamp', 'created_at', 'date_created', 'log_time', 'datetime']
                            timestamp_col = None
                            
                            for col in timestamp_cols:
                                if col in table_info['columns']:
                                    timestamp_col = col
                                    break
                            
                            if timestamp_col:
                                # Copy recent records only
                                old_cursor.execute(f"SELECT * FROM {table_name} WHERE {timestamp_col} >= ? ORDER BY {timestamp_col} DESC LIMIT 100", 
                                                 (cutoff_timestamp,))
                            else:
                                # Copy last 100 records
                                old_cursor.execute(f"SELECT * FROM {table_name} ORDER BY rowid DESC LIMIT 100")
                                
                        elif 'template' in table_name.lower() or 'script' in table_name.lower():
                            # Keep essential templates and scripts
                            old_cursor.execute(f"SELECT * FROM {table_name} ORDER BY rowid DESC LIMIT 200")
                            
                        else:
                            # Keep all records for other tables (likely small)
                            old_cursor.execute(f"SELECT * FROM {table_name}")
                        
                        # Insert records into new database
                        records = old_cursor.fetchall()
                        if records:
                            placeholders = ','.join(['?' for _ in range(len(table_info['columns']))])
                            new_cursor.executemany(f"INSERT INTO {table_name} VALUES ({placeholders})", records)
                            print(f"✅ Copied {len(records)} records to {table_name}")
                        
                    new_conn.commit()
                    
        except Exception as e:
            print(f"❌ Database creation failed: {e}")
            return False
            
        return True
        
    def replace_original_database(self):
        """🔄 Replace original database with optimized version"""
        try:
            # Create backup of original
            shutil.copy2(str(self.old_db_path), str(self.backup_path))
            print(f"💾 Backup created: {self.backup_path}")
            
            # Replace original with optimized
            shutil.move(str(self.new_db_path), str(self.old_db_path))
            print(f"🔄 Database replaced successfully")
            
            return True
            
        except Exception as e:
            print(f"❌ Database replacement failed: {e}")
            return False
            
    def execute_rebuild(self):
        """🚀 Execute complete database rebuild process"""
        
        # Get initial size
        initial_size = self.old_db_path.stat().st_size
        initial_size_mb = initial_size / (1024 * 1024)
        
        with tqdm(total=100, desc="🔄 Database Rebuild", unit="%") as pbar:
            
            # Phase 1: Analyze (25%)
            pbar.set_description("🔍 Analyzing source database")
            analysis = self.analyze_source_database()
            pbar.update(25)
            
            # Phase 2: Create optimized (50%)
            pbar.set_description("🏗️ Creating optimized database")
            success = self.create_optimized_database(analysis)
            if not success:
                raise RuntimeError("Failed to create optimized database")
            pbar.update(50)
            
            # Phase 3: Replace original (25%)
            pbar.set_description("🔄 Replacing original database")
            success = self.replace_original_database()
            if not success:
                raise RuntimeError("Failed to replace original database")
            pbar.update(25)
            
        # Get final size
        final_size = self.old_db_path.stat().st_size
        final_size_mb = final_size / (1024 * 1024)
        
        # Calculate savings
        size_reduction = initial_size - final_size
        size_reduction_mb = size_reduction / (1024 * 1024)
        reduction_percent = (size_reduction / initial_size) * 100
        
        print("="*80)
        print("📊 REBUILD RESULTS:")
        print(f"   Initial Size: {initial_size_mb:.1f} MB")
        print(f"   Final Size: {final_size_mb:.1f} MB")
        print(f"   Size Reduction: {size_reduction_mb:.1f} MB ({reduction_percent:.1f}%)")
        print(f"   Target Achieved: {'✅ YES' if final_size <= self.max_size_bytes else '❌ NO'}")
        print(f"   Backup Available: {self.backup_path}")
        print("="*80)
        
        duration = (datetime.now() - self.start_time).total_seconds()
        print(f"⏱️ Total Duration: {duration:.2f} seconds")
        
        return {
            'initial_size_mb': initial_size_mb,
            'final_size_mb': final_size_mb,
            'reduction_mb': size_reduction_mb,
            'reduction_percent': reduction_percent,
            'target_achieved': final_size <= self.max_size_bytes,
            'backup_path': str(self.backup_path)
        }

if __name__ == "__main__":
    rebuilder = DeploymentLogsRebuilder()
    result = rebuilder.execute_rebuild()
    
    print("✅ DATABASE REBUILD COMPLETE")
