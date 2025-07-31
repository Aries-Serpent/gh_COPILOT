#!/usr/bin/env python3
"""
🗄️ Database Migration Engine
============================
Migrate databases from root to databases folder with conflict resolution
"""

import os
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path
import hashlib


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


def get_database_info(db_path):
    """Get basic info about a SQLite database"""
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()

            # Get file size
            file_size = os.path.getsize(db_path)

            # Get modification time
            mod_time = datetime.fromtimestamp(os.path.getmtime(db_path))

            return {
                "tables": [table[0] for table in tables],
                "table_count": len(tables),
                "file_size": file_size,
                "modified": mod_time,
                "file_path": db_path,
            }
    except Exception as e:
        print(f"❌ Error reading database {db_path}: {e}")
        return None


def migrate_databases():
    """🗄️ Migrate databases from root to databases folder"""
    start_time = datetime.now()
    print(f"🗄️ DATABASE MIGRATION ENGINE")
    print(f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    workspace_root = Path("e:/gh_COPILOT")
    databases_folder = workspace_root / "databases"

    # Ensure databases folder exists
    databases_folder.mkdir(exist_ok=True)

    # Find database files in root
    root_databases = []
    for file in workspace_root.iterdir():
        if file.is_file() and file.suffix == ".db":
            root_databases.append(file)

    print(f"🔍 Found {len(root_databases)} database(s) in root folder:")
    for db in root_databases:
        print(f"   📄 {db.name}")

    migration_results = []

    for root_db in root_databases:
        print(f"\n🔄 Processing: {root_db.name}")
        print("-" * 50)

        target_db = databases_folder / root_db.name

        # Get info about root database
        root_info = get_database_info(root_db)
        if not root_info:
            print(f"❌ Cannot read root database {root_db.name}, skipping")
            continue

        print(f"📊 Root DB Info:")
        print(f"   📁 Size: {root_info['file_size']:,} bytes")
        print(f"   📅 Modified: {root_info['modified']}")
        print(f"   🗃️ Tables: {root_info['table_count']}")

        # Check if target already exists
        if target_db.exists():
            target_info = get_database_info(target_db)
            if target_info:
                print(f"📊 Target DB Info:")
                print(f"   📁 Size: {target_info['file_size']:,} bytes")
                print(f"   📅 Modified: {target_info['modified']}")
                print(f"   🗃️ Tables: {target_info['table_count']}")

                # Calculate hashes to check if files are identical
                root_hash = calculate_file_hash(root_db)
                target_hash = calculate_file_hash(target_db)

                if root_hash == target_hash:
                    print(f"✅ Files are identical - safe to remove root database")
                    action = "remove_duplicate"
                elif root_info["modified"] > target_info["modified"]:
                    print(f"⚠️  Root database is newer - creating backup and replacing")
                    action = "replace_with_backup"
                elif root_info["file_size"] > target_info["file_size"]:
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
                root_db.unlink()
                print(f"✅ Removed duplicate database from root")
                result = "removed_duplicate"

            elif action == "move":
                # Simple move
                shutil.move(str(root_db), str(target_db))
                print(f"✅ Moved database to databases folder")
                result = "moved"

            elif action == "replace":
                # Replace target with root
                shutil.move(str(root_db), str(target_db))
                print(f"✅ Replaced target database")
                result = "replaced"

            elif action == "replace_with_backup":
                # Backup target and replace with root
                backup_name = f"{target_db.stem}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
                backup_path = databases_folder / backup_name
                shutil.copy2(str(target_db), str(backup_path))
                print(f"📦 Created backup: {backup_name}")

                shutil.move(str(root_db), str(target_db))
                print(f"✅ Replaced target database with root version")
                result = "replaced_with_backup"

            elif action == "backup_root":
                # Backup root version
                backup_name = f"{root_db.stem}_root_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
                backup_path = databases_folder / backup_name
                shutil.copy2(str(root_db), str(backup_path))
                print(f"📦 Created backup of root: {backup_name}")

                root_db.unlink()
                print(f"✅ Removed root database (backup preserved)")
                result = "backed_up_root"

        except Exception as e:
            print(f"❌ Error during migration: {e}")
            result = "error"

        migration_results.append({"database": root_db.name, "action": action, "result": result})

    # Summary
    duration = (datetime.now() - start_time).total_seconds()
    print(f"\n🗄️ MIGRATION SUMMARY:")
    print("=" * 50)

    for result in migration_results:
        status = "✅" if result["result"] != "error" else "❌"
        print(f"{status} {result['database']}: {result['result']}")

    print(f"\n📊 Migration Statistics:")
    print(f"   📄 Databases processed: {len(migration_results)}")
    print(f"   ✅ Successful: {sum(1 for r in migration_results if r['result'] != 'error')}")
    print(f"   ❌ Errors: {sum(1 for r in migration_results if r['result'] == 'error')}")
    print(f"   ⏱️ Duration: {duration:.2f} seconds")

    # Verify final state
    print(f"\n🔍 FINAL VERIFICATION:")
    print("-" * 30)

    remaining_root_dbs = [f for f in workspace_root.iterdir() if f.is_file() and f.suffix == ".db"]
    if remaining_root_dbs:
        print(f"⚠️  {len(remaining_root_dbs)} database(s) still in root:")
        for db in remaining_root_dbs:
            print(f"   📄 {db.name}")
    else:
        print(f"✅ No databases remaining in root folder")

    target_dbs = [f for f in databases_folder.iterdir() if f.is_file() and f.suffix == ".db"]
    print(f"📁 {len(target_dbs)} database(s) in databases folder")

    print(f"\n🏆 DATABASE MIGRATION COMPLETE!")
    return migration_results


if __name__ == "__main__":
    migrate_databases()
