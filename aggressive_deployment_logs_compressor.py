#!/usr/bin/env python3
"""
🔥 AGGRESSIVE DEPLOYMENT LOGS DATABASE COMPRESSOR
================================================================
MISSION: Reduce deployment_logs.db from 141MB to below 99.9MB
while maintaining essential functionality and logs
================================================================
"""

import sqlite3
import os
from datetime import datetime, timedelta
from pathlib import Path
from tqdm import tqdm
import time

class AggressiveDeploymentLogsCompressor:
    """🔥 Aggressive Database Compression for deployment_logs.db"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.db_path = Path("e:/gh_COPILOT/databases/deployment_logs.db")
        self.max_size_mb = 99.9
        self.max_size_bytes = int(self.max_size_mb * 1024 * 1024)
        
        print("="*80)
        print("🔥 AGGRESSIVE DEPLOYMENT LOGS DATABASE COMPRESSOR")
        print(f"🚀 Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📁 Target Database: {self.db_path}")
        print(f"📏 Target Size: {self.max_size_mb} MB ({self.max_size_bytes:,} bytes)")
        print("="*80)
        
    def analyze_database_structure(self):
        """🔍 Analyze database tables and sizes"""
        analysis = {
            'tables': [],
            'total_size': 0,
            'largest_tables': []
        }
        
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                
                # Get all tables
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                
                for table_name, in tables:
                    # Get table info
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    row_count = cursor.fetchone()[0]
                    
                    # Estimate table size (rough approximation)
                    cursor.execute(f"PRAGMA table_info({table_name})")
                    columns = cursor.fetchall()
                    
                    table_info = {
                        'name': table_name,
                        'row_count': row_count,
                        'column_count': len(columns),
                        'estimated_size_per_row': len(columns) * 50  # rough estimate
                    }
                    table_info['estimated_total_size'] = table_info['row_count'] * table_info['estimated_size_per_row']
                    analysis['tables'].append(table_info)
                
                # Sort by estimated size
                analysis['largest_tables'] = sorted(analysis['tables'], 
                                                  key=lambda x: x['estimated_total_size'], 
                                                  reverse=True)
                
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            
        return analysis
        
    def compress_deployment_logs_aggressively(self):
        """🔥 Aggressive compression of deployment logs"""
        
        with tqdm(total=100, desc="🔥 Aggressive Compression", unit="%") as pbar:
            
            # Phase 1: Analyze structure (20%)
            pbar.set_description("🔍 Analyzing database structure")
            analysis = self.analyze_database_structure()
            pbar.update(20)
            
            # Phase 2: Remove old logs (30%)
            pbar.set_description("🗑️ Removing old logs")
            self.remove_old_logs()
            pbar.update(30)
            
            # Phase 3: Aggressive VACUUM (25%)
            pbar.set_description("🗜️ Aggressive VACUUM")
            self.aggressive_vacuum()
            pbar.update(25)
            
            # Phase 4: Final optimization (25%)
            pbar.set_description("⚡ Final optimization")
            self.final_optimization()
            pbar.update(25)
            
        return analysis
        
    def remove_old_logs(self):
        """🗑️ Remove logs older than 30 days"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                
                # Get cutoff date (30 days ago)
                cutoff_date = datetime.now() - timedelta(days=30)
                cutoff_timestamp = cutoff_date.isoformat()
                
                # Find tables with timestamp/date columns
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                
                for table_name, in tables:
                    try:
                        # Try common timestamp column names
                        timestamp_columns = ['timestamp', 'created_at', 'date_created', 'log_time', 'datetime']
                        
                        for col in timestamp_columns:
                            try:
                                # Check if column exists
                                cursor.execute(f"PRAGMA table_info({table_name})")
                                columns = [info[1] for info in cursor.fetchall()]
                                
                                if col in columns:
                                    # Delete old records
                                    cursor.execute(f"DELETE FROM {table_name} WHERE {col} < ?", (cutoff_timestamp,))
                                    deleted = cursor.rowcount
                                    if deleted > 0:
                                        print(f"🗑️ Deleted {deleted} old records from {table_name}")
                                    break
                            except sqlite3.Error:
                                continue
                                
                    except sqlite3.Error as e:
                        print(f"⚠️ Could not clean table {table_name}: {e}")
                        continue
                
                conn.commit()
                
        except Exception as e:
            print(f"❌ Log removal failed: {e}")
            
    def aggressive_vacuum(self):
        """🗜️ Aggressive database vacuum and compression"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                # Enable aggressive settings
                conn.execute('PRAGMA journal_mode=DELETE')
                conn.execute('PRAGMA page_size=4096')
                conn.execute('PRAGMA auto_vacuum=FULL')
                conn.execute('PRAGMA shrink_memory')
                
                # Full vacuum
                conn.execute('VACUUM')
                
                # Reanalyze
                conn.execute('ANALYZE')
                
                # Optimize
                conn.execute('PRAGMA optimize')
                
                conn.commit()
                
        except Exception as e:
            print(f"❌ Aggressive vacuum failed: {e}")
            
    def final_optimization(self):
        """⚡ Final database optimization"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                
                # Drop any temporary tables
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'temp_%'")
                temp_tables = cursor.fetchall()
                
                for table_name, in temp_tables:
                    cursor.execute(f"DROP TABLE {table_name}")
                    print(f"🗑️ Dropped temporary table: {table_name}")
                
                # Compact database
                conn.execute('PRAGMA incremental_vacuum')
                conn.execute('PRAGMA shrink_memory')
                
                conn.commit()
                
        except Exception as e:
            print(f"❌ Final optimization failed: {e}")
            
    def execute_compression(self):
        """🚀 Execute complete compression process"""
        
        # Get initial size
        initial_size = self.db_path.stat().st_size
        initial_size_mb = initial_size / (1024 * 1024)
        
        print(f"📊 Initial Size: {initial_size_mb:.1f} MB")
        
        # Execute compression
        analysis = self.compress_deployment_logs_aggressively()
        
        # Get final size
        final_size = self.db_path.stat().st_size
        final_size_mb = final_size / (1024 * 1024)
        
        # Calculate savings
        size_reduction = initial_size - final_size
        size_reduction_mb = size_reduction / (1024 * 1024)
        reduction_percent = (size_reduction / initial_size) * 100
        
        print("="*80)
        print("📊 COMPRESSION RESULTS:")
        print(f"   Initial Size: {initial_size_mb:.1f} MB")
        print(f"   Final Size: {final_size_mb:.1f} MB")
        print(f"   Size Reduction: {size_reduction_mb:.1f} MB ({reduction_percent:.1f}%)")
        print(f"   Target Achieved: {'✅ YES' if final_size <= self.max_size_bytes else '❌ NO'}")
        print("="*80)
        
        # If still too large, suggest manual intervention
        if final_size > self.max_size_bytes:
            print("⚠️ DATABASE STILL TOO LARGE - MANUAL INTERVENTION REQUIRED")
            print("Suggested actions:")
            print("1. Archive old deployment logs to external storage")
            print("2. Implement log rotation policy")
            print("3. Consider splitting into multiple smaller databases")
            
            # Show largest tables for manual cleanup
            if analysis['largest_tables']:
                print("\n📊 LARGEST TABLES (for manual cleanup):")
                for table in analysis['largest_tables'][:5]:
                    print(f"   - {table['name']}: {table['row_count']:,} rows")
        
        duration = (datetime.now() - self.start_time).total_seconds()
        print(f"⏱️ Total Duration: {duration:.2f} seconds")
        
        return {
            'initial_size_mb': initial_size_mb,
            'final_size_mb': final_size_mb,
            'reduction_mb': size_reduction_mb,
            'reduction_percent': reduction_percent,
            'target_achieved': final_size <= self.max_size_bytes
        }

if __name__ == "__main__":
    compressor = AggressiveDeploymentLogsCompressor()
    result = compressor.execute_compression()
    
    print("✅ AGGRESSIVE COMPRESSION COMPLETE")
