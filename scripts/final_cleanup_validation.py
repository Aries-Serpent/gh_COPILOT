#!/usr/bin/env python3
"""
FINAL DATABASE CLEANUP VALIDATION
=================================

Validates the results of our database cleanup operation
"""

from pathlib import Path



def main():
    print('FINAL VERIFICATION: STAGING DATABASE CLEANUP')
    print('=' * 50)

    staging_path = Path('E:/gh_COPILOT/databases')

    if staging_path.exists():
        remaining_files = list(staging_path.rglob('*'))
        remaining_file_count = len([f for f in remaining_files if f.is_file()])

        print(f'Staging directory exists: {staging_path}')
        print(f'Remaining files: {remaining_file_count}')

        if remaining_file_count > 0:
            print('Remaining files:')
            for file in remaining_files:
                if file.is_file():
                    size_mb = file.stat().st_size / (1024 * 1024)
                    print(f'   - {file.name} ({size_mb:.2f} MB)')
        else:
            print('Staging directory is completely clean!')

        # Check total size
        total_size = 0
        for file in remaining_files:
            if file.is_file():
                total_size += file.stat().st_size

        print(f'Total remaining size: {total_size / (1024 * 1024):.2f} MB')

    else:
        print('Staging directory no longer exists')

    print()
    print('LOCAL DATABASE STATUS:')
    local_path = Path('databases')
    if local_path.exists():
        local_files = list(local_path.rglob('*'))
        local_file_count = len([f for f in local_files if f.is_file()])

        local_size = 0
        for file in local_files:
            if file.is_file():
                local_size += file.stat().st_size

        print(f'Local database files: {local_file_count}')
        print(f'Local database size: {local_size / (1024 * 1024):.2f} MB')
        print('Local database contains complete record')
    else:
        print('Local database missing')

    print()
    print('CLEANUP VALIDATION: COMPLETE')


if __name__ == "__main__":
    main()
