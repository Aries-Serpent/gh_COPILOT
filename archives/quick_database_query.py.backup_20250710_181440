#!/usr/bin/env python3
"""
Quick Database Query Tool
========================
Query all databases in the codebase to show structure and sample dat"a""
"""
import sqlite3
import os
from pathlib import Path


def query_database(db_path):
  " "" """Query a single database and return its structure and sample da"t""a"""
    results = {
     " "" 'tabl'e''s': {},
      ' '' 'stat'u''s'':'' 'succe's''s',
      ' '' 'err'o''r': None
    }

        try:
    conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get all user tables (excluding sqlite_ tables)
        cursor.execute(
  ' '' "SELECT name FROM sqlite_master WHERE typ"e""='tab'l''e' AND name NOT LIK'E'' 'sqlite'_''%'")
        table_names = [row[0] for row in cursor.fetchall()]

        for table_name in table_names:
            # Get row count
    cursor.execute"(""f"SELECT COUNT(*) FROM {table_nam"e""}")
            row_count = cursor.fetchone()[0]

            # Get column info
            cursor.execute"(""f"PRAGMA table_info({table_name"}"")")
            columns = [col[1] for col in cursor.fetchall()]

            # Get sample data (first 2 rows)
            cursor.execute"(""f"SELECT * FROM {table_name} LIMIT" ""2")
            sample_data = cursor.fetchall()

            result"s""['tabl'e''s'][table_name] = {
    }

        conn.close()

        except Exception as e:
    result's''['stat'u''s'] '='' 'err'o''r'
        result's''['err'o''r'] = str(e)

        return results


    def main():
    databases_dir = Pat'h''('databas'e''s')

    if not databases_dir.exists():
    prin't''("[ERROR] databases directory not fou"n""d")
        return

    prin"t""("[SEARCH] QUICK DATABASE QUERY RESUL"T""S")
    prin"t""("""=" * 60)

    for db_file in sorted(databases_dir.glo"b""('*.'d''b')):
    result = query_database(db_file)

        print'(''f"\n[BAR_CHART] {resul"t""['na'm''e'']''}")
        prin"t""("""-" * 40)

        if resul"t""['stat'u''s'] ='='' 'err'o''r':
    print'(''f"[ERROR] Error: {resul"t""['err'o''r'']''}")
            continue

        if not resul"t""['tabl'e''s']:
    prin't''("[NOTES] No user tables fou"n""d")
            continue

        for table_name, table_info in resul"t""['tabl'e''s'].items():
    print'(''f"[CLIPBOARD] Table: {table_nam"e""}")
            print"(""f"   Records: {table_inf"o""['row_cou'n''t'']''}")
            print(
   " ""f"   Columns:" ""{'','' '.join(table_inf'o''['colum'n''s'][:5])'}''{'.'.''.' if len(table_inf'o''['colum'n''s']) > 5 els'e'' ''''}")

            if table_inf"o""['sample_da't''a']:
    print(
   ' ''f"   Sample: {str(table_inf"o""['sample_da't''a'][0])[:80]}.'.''.")
            print()


    if __name__ ="="" "__main"_""_":
    main()"
""