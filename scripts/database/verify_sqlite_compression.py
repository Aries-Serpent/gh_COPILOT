#!/usr/bin/env python3
"""
Quick SQLite Database Verification
"""

import sqlite3

def verify_sqlite_database():
    """Verify the compressed SQLite database"""
    
    print("🗄️ SQLite Database Verification:")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect('databases/database_validation_results.db')
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"📊 Tables created: {len(tables)}")
        for table in tables:
            print(f"   - {table[0]}")
        
        # Check data counts
        for table_name in ['validation_summary', 'database_info', 'compression_metadata']:
            try:
                cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
                count = cursor.fetchone()[0]
                print(f"📋 {table_name}: {count} records")
            except Exception as e:
                print(f"❌ {table_name}: {e}")
        
        # Check compression metadata
        cursor.execute('SELECT original_size_mb, compression_ratio FROM compression_metadata LIMIT 1')
        metadata = cursor.fetchone()
        if metadata:
            print(f"🗜️ Original size: {metadata[0]:.2f} MB")
            print(f"🎯 Compression ratio: {metadata[1]:.2f}%")
        
        # Sample data verification
        cursor.execute('SELECT key_name, record_count FROM validation_summary LIMIT 5')
        samples = cursor.fetchall()
        print("\n📋 Sample validation data:")
        for sample in samples:
            print(f"   - {sample[0]}: {sample[1]} records")
        
        conn.close()
        print("\n✅ Verification complete - Database is functional!")
        return True
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

if __name__ == "__main__":
    verify_sqlite_database()
