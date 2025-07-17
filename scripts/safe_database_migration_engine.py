#!/usr/bin/env python3
"""
🗄️ Safe Database Migration Engine
=================================
Safely migrate databases with connection handling
"""

import os
import shutil
import sqlite3
import gc
import time
from datetime import datetime
from pathlib import Path
import hashlib

def force_close_connections():
    """Force garbage collection to close any lingering database connections"""
    gc.collect()
    time.sleep(0.5)  # Give time for cleanup

def safe_database_operation(db_path, operation_func):
    """Safely perform database operation with connection cleanup"""
    try:
        # Force cleanup first
        force_close_connections()
        
        # Try the operation
        return operation_func(db_path)
    except sqlite3.OperationalError as e:
        if "database is locked" in str(e).lower():
            print(f"⚠️  Database locked, waiting...")
            time.sleep(2)
            force_close_connections()
            return operation_func(db_path)
        else:
            raise e

def get_database_info_safe(db_path):
    """Safely get database info with connection handling"""
    def _get_info(path):
        # Use a very short-lived connection
        conn = sqlite3.connect(str(path), timeout=1.0)
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            return {
                'tables': [table[0] for table in tables],
                'table_count': len(tables),
                'file_size': os.path.getsize(path),
                'modified': datetime.fromtimestamp(os.path.getmtime(path))
            }
        finally:
            conn.close()
    
    try:
        return safe_database_operation(db_path, _get_info)
    except Exception as e:
        print(f"❌ Cannot read database {db_path}: {e}")
        # Return basic file info only
        try:
            return {
                'tables': [],
                'table_count': 0,
                'file_size': os.path.getsize(db_path),
                'modified': datetime.fromtimestamp(os.path.getmtime(db_path))
            }
        except:
            return None

def calculate_file_hash(file_path):
    """Calculate SHA-256 hash of a file"""
    hash_sha256 = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    except Exception as e:
        print(f"❌ Error calculating hash for {file_path}: {e}")
        return None

def safe_file_move(source, target):
    """Safely move a file with retries"""
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            force_close_connections()
            
            # Check if we can access the file
            if os.path.exists(source):
                # Try to copy first, then delete original
                shutil.copy2(source, target)
                time.sleep(0.5)  # Give time for the copy to complete
                os.remove(source)
                return True
            else:
                print(f"⚠️  Source file no longer exists: {source}")
                return False
                
        except PermissionError as e:
            print(f"⚠️  Attempt {attempt + 1}: Permission error - {e}")
            if attempt < max_attempts - 1:
                time.sleep(2)
            else:
                return False
        except Exception as e:
            print(f"❌ Move failed: {e}")
            return False
    
    return False

def migrate_databases_safe():
    """🗄️ Safely migrate databases from root to databases folder"""
    start_time = datetime.now()
    print(f"🗄️ SAFE DATABASE MIGRATION ENGINE")
    print(f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    workspace_root = Path("e:/gh_COPILOT")
    databases_folder = workspace_root / "databases"
    
    # Ensure databases folder exists
    databases_folder.mkdir(exist_ok=True)
    
    # Find database files in root
    root_databases = []
    for file in workspace_root.iterdir():
        if file.is_file() and file.suffix == '.db':
            root_databases.append(file)
    
    print(f"🔍 Found {len(root_databases)} database(s) in root folder:")
    for db in root_databases:
        print(f"   📄 {db.name}")
    
    if not root_databases:
        print(f"✅ No databases found in root - migration not needed")
        return []
    
    # Force any cleanup before starting
    print(f"\n🧹 Cleaning up any open connections...")
    force_close_connections()
    
    migration_results = []
    
    for root_db in root_databases:
        print(f"\n🔄 Processing: {root_db.name}")
        print("-" * 50)
        
        target_db = databases_folder / root_db.name
        
        # Get info about root database (safely)
        root_info = get_database_info_safe(root_db)
        if not root_info:
            print(f"❌ Cannot access root database {root_db.name}, skipping")
            migration_results.append({
                'database': root_db.name,
                'action': 'skip',
                'result': 'inaccessible'
            })
            continue
            
        print(f"📊 Root DB Info:")
        print(f"   📁 Size: {root_info['file_size']:,} bytes")
        print(f"   📅 Modified: {root_info['modified']}")
        print(f"   🗃️ Tables: {root_info['table_count']}")
        
        # Check if target already exists
        if target_db.exists():
            target_info = get_database_info_safe(target_db)
            if target_info:
                print(f"📊 Target DB Info:")
                print(f"   📁 Size: {target_info['file_size']:,} bytes")
                print(f"   📅 Modified: {target_info['modified']}")
                print(f"   🗃️ Tables: {target_info['table_count']}")
                
                # Calculate hashes to check if files are identical
                root_hash = calculate_file_hash(root_db)
                target_hash = calculate_file_hash(target_db)
                
                if root_hash and target_hash and root_hash == target_hash:
                    print(f"✅ Files are identical - safe to remove root database")
                    action = "remove_duplicate"
                elif root_info['modified'] > target_info['modified']:
                    print(f"⚠️  Root database is newer - creating backup and replacing")
                    action = "replace_with_backup"
                elif root_info['file_size'] > target_info['file_size']:
                    print(f"⚠️  Root database is larger - creating backup and replacing")
                    action = "replace_with_backup"
                else:
                    print(f"⚠️  Target database appears current - backing up root")
                    action = "backup_root"
            else:
                print(f"❌ Cannot read target database - will replace")
                action = "replace"
        else:
            print(f"✅ No conflict - will move database")
            action = "move"
        
        # Execute migration action
        try:
            if action == "remove_duplicate":
                # Files are identical, just remove the root copy
                force_close_connections()
                time.sleep(0.5)
                if os.path.exists(root_db):
                    os.remove(root_db)
                    print(f"✅ Removed duplicate database from root")
                    result = "removed_duplicate"
                else:
                    result = "already_removed"
                
            elif action == "move":
                # Simple move
                if safe_file_move(str(root_db), str(target_db)):
                    print(f"✅ Moved database to databases folder")
                    result = "moved"
                else:
                    print(f"❌ Failed to move database")
                    result = "move_failed"
                
            elif action == "replace":
                # Replace target with root
                if target_db.exists():
                    os.remove(target_db)
                    time.sleep(0.5)
                
                if safe_file_move(str(root_db), str(target_db)):
                    print(f"✅ Replaced target database")
                    result = "replaced"
                else:
                    print(f"❌ Failed to replace database")
                    result = "replace_failed"
                
            elif action == "replace_with_backup":
                # Backup target and replace with root
                backup_name = f"{target_db.stem}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
                backup_path = databases_folder / backup_name
                
                shutil.copy2(str(target_db), str(backup_path))
                print(f"📦 Created backup: {backup_name}")
                time.sleep(0.5)
                
                os.remove(target_db)
                time.sleep(0.5)
                
                if safe_file_move(str(root_db), str(target_db)):
                    print(f"✅ Replaced target database with root version")
                    result = "replaced_with_backup"
                else:
                    print(f"❌ Failed to replace database (backup preserved)")
                    result = "replace_backup_failed"
                
            elif action == "backup_root":
                # Backup root version
                backup_name = f"{root_db.stem}_root_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
                backup_path = databases_folder / backup_name
                
                shutil.copy2(str(root_db), str(backup_path))
                print(f"📦 Created backup of root: {backup_name}")
                time.sleep(0.5)
                
                force_close_connections()
                os.remove(root_db)
                print(f"✅ Removed root database (backup preserved)")
                result = "backed_up_root"
                
        except Exception as e:
            print(f"❌ Error during migration: {e}")
            result = "error"
        
        migration_results.append({
            'database': root_db.name,
            'action': action,
            'result': result
        })
    
    # Summary
    duration = (datetime.now() - start_time).total_seconds()
    print(f"\n🗄️ MIGRATION SUMMARY:")
    print("=" * 50)
    
    for result in migration_results:
        status = "✅" if "failed" not in result['result'] and result['result'] != "error" else "❌"
        print(f"{status} {result['database']}: {result['result']}")
    
    print(f"\n📊 Migration Statistics:")
    print(f"   📄 Databases processed: {len(migration_results)}")
    successful = sum(1 for r in migration_results if "failed" not in r['result'] and r['result'] != 'error')
    print(f"   ✅ Successful: {successful}")
    print(f"   ❌ Errors: {len(migration_results) - successful}")
    print(f"   ⏱️ Duration: {duration:.2f} seconds")
    
    # Verify final state
    print(f"\n🔍 FINAL VERIFICATION:")
    print("-" * 30)
    
    remaining_root_dbs = [f for f in workspace_root.iterdir() if f.is_file() and f.suffix == '.db']
    if remaining_root_dbs:
        print(f"⚠️  {len(remaining_root_dbs)} database(s) still in root:")
        for db in remaining_root_dbs:
            print(f"   📄 {db.name}")
    else:
        print(f"✅ No databases remaining in root folder")
    
    target_dbs = [f for f in databases_folder.iterdir() if f.is_file() and f.suffix == '.db']
    print(f"📁 {len(target_dbs)} database(s) in databases folder")
    
    print(f"\n🏆 SAFE DATABASE MIGRATION COMPLETE!")
    return migration_results

if __name__ == "__main__":
    migrate_databases_safe()
