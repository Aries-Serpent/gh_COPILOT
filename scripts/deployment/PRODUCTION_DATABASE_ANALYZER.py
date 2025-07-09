#!/usr/bin/env python3
"""
PRODUCTION DATABASE ANALYSIS SCRIPT
==================================
Enterprise-grade analysis of duplicate production.db files
Determines correct handling approach for database consolidatio"n""
"""

import sqlite3
import os
import json
import hashlib
from datetime import datetime
from pathlib import Path


def get_file_hash(filepath):
  " "" """Calculate SHA256 hash of fi"l""e"""
    hash_sha256 = hashlib.sha256()
    try:
        with open(filepath","" ""r""b") as f:
            for chunk in iter(lambda: f.read(4096)," ""b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    except Exception as e:
        return" ""f"ERROR: {str(e")""}"


def analyze_database_structure(db_path):
  " "" """Analyze database structure and conten"t""s"""
    analysis = {
      " "" "file_pa"t""h": str(db_path),
      " "" "file_si"z""e": 0,
      " "" "last_modifi"e""d": None,
      " "" "tabl"e""s": [],
      " "" "record_coun"t""s": {},
      " "" "schema_in"f""o": {},
      " "" "connection_stat"u""s"":"" "UNKNO"W""N",
      " "" "ha"s""h": None
    }

    try:
        # File stats
        stat = os.stat(db_path)
        analysi"s""["file_si"z""e"] = stat.st_size
        analysi"s""["last_modifi"e""d"] = datetime.fromtimestamp(]
            stat.st_mtime).isoformat()
        analysi"s""["ha"s""h"] = get_file_hash(db_path)

        # Database analysis
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get all tables
        cursor.execut"e""("SELECT name FROM sqlite_master WHERE typ"e""='tab'l''e''';")
        tables = cursor.fetchall()
        analysi"s""["tabl"e""s"] = [table[0] for table in tables]

        # Get record counts for each table
        for table in analysi"s""["tabl"e""s"]:
            try:
                cursor.execute"(""f"SELECT COUNT(*) FROM {tabl"e""}")
                count = cursor.fetchone()[0]
                analysi"s""["record_coun"t""s"][table] = count
            except Exception as e:
                analysi"s""["record_coun"t""s"][table] =" ""f"ERROR: {str(e")""}"
        # Get schema info
        for table in analysi"s""["tabl"e""s"]:
            try:
                cursor.execute"(""f"PRAGMA table_info({table"}"")")
                columns = cursor.fetchall()
                analysi"s""["schema_in"f""o"][table] = [
                      " "" "column_na"m""e": col[1],
                      " "" "data_ty"p""e": col[2],
                      " "" "not_nu"l""l": bool(col[3]),
                      " "" "primary_k"e""y": bool(col[5])
                    }
                    for col in columns
                ]
            except Exception as e:
                analysi"s""["schema_in"f""o"][table] =" ""f"ERROR: {str(e")""}"
        analysi"s""["connection_stat"u""s"] "="" "SUCCE"S""S"
        conn.close()

    except Exception as e:
        analysi"s""["connection_stat"u""s"] =" ""f"ERROR: {str(e")""}"
    return analysis


def compare_databases(db1_analysis, db2_analysis):
  " "" """Compare two database analys"e""s"""
    comparison = {
      " "" "timesta"m""p": datetime.now().isoformat(),
      " "" "file_comparis"o""n": {]
              " "" "pa"t""h": db1_analysi"s""["file_pa"t""h"],
              " "" "si"z""e": db1_analysi"s""["file_si"z""e"],
              " "" "modifi"e""d": db1_analysi"s""["last_modifi"e""d"],
              " "" "ha"s""h": db1_analysi"s""["ha"s""h"]
            },
          " "" "d"b""2": {]
              " "" "pa"t""h": db2_analysi"s""["file_pa"t""h"],
              " "" "si"z""e": db2_analysi"s""["file_si"z""e"],
              " "" "modifi"e""d": db2_analysi"s""["last_modifi"e""d"],
              " "" "ha"s""h": db2_analysi"s""["ha"s""h"]
            }
        },
      " "" "identical_fil"e""s": False,
      " "" "size_differen"c""e": abs(db1_analysi"s""["file_si"z""e"] - db2_analysi"s""["file_si"z""e"]),
      " "" "table_comparis"o""n": {]
          " "" "db1_tabl"e""s": db1_analysi"s""["tabl"e""s"],
          " "" "db2_tabl"e""s": db2_analysi"s""["tabl"e""s"],
          " "" "common_tabl"e""s": [],
          " "" "db1_on"l""y": [],
          " "" "db2_on"l""y": []
        },
      " "" "record_comparis"o""n": {},
      " "" "recommendatio"n""s": []
    }

    # Check if files are identical
    if db1_analysi"s""["ha"s""h"] == db2_analysi"s""["ha"s""h"]:
        compariso"n""["identical_fil"e""s"] = True

    # Compare tables
    db1_tables = set(db1_analysi"s""["tabl"e""s"])
    db2_tables = set(db2_analysi"s""["tabl"e""s"])

    compariso"n""["table_comparis"o""n""]""["common_tabl"e""s"] = list(]
        db1_tables & db2_tables)
    compariso"n""["table_comparis"o""n""]""["db1_on"l""y"] = list(db1_tables - db2_tables)
    compariso"n""["table_comparis"o""n""]""["db2_on"l""y"] = list(db2_tables - db1_tables)

    # Compare record counts for common tables
    for table in compariso"n""["table_comparis"o""n""]""["common_tabl"e""s"]:
        if table in db1_analysi"s""["record_coun"t""s"] and table in db2_analysi"s""["record_coun"t""s"]:
            compariso"n""["record_comparis"o""n"][table] = {
              " "" "db1_cou"n""t": db1_analysi"s""["record_coun"t""s"][table],
              " "" "db2_cou"n""t": db2_analysi"s""["record_coun"t""s"][table],
              " "" "differen"c""e": abs(]
                    int(db1_analysi"s""["record_coun"t""s"][table]) -
                    int(db2_analysi"s""["record_coun"t""s"][table])
                ) if isinstance(db1_analysi"s""["record_coun"t""s"][table], int) and isinstance(db2_analysi"s""["record_coun"t""s"][table], int) els"e"" "N"/""A"
            }

    # Generate recommendations
    if compariso"n""["identical_fil"e""s"]:
        compariso"n""["recommendatio"n""s"].append(]
          " "" "recommended_acti"o""n"":"" "Keep database in /databases/ folder (proper enterprise locatio"n"")"
        })
    else:
        if db1_analysi"s""["file_si"z""e"] > db2_analysi"s""["file_si"z""e"]:
            compariso"n""["recommendatio"n""s"].append(]
              " "" "descripti"o""n":" ""f"Root database is {compariso"n""['size_differen'c''e']} bytes larg'e''r",
              " "" "recommended_acti"o""n"":"" "Root database appears to have more da"t""a"
            })
        elif db2_analysi"s""["file_si"z""e"] > db1_analysi"s""["file_si"z""e"]:
            compariso"n""["recommendatio"n""s"].append(]
              " "" "descripti"o""n":" ""f"Databases database is {compariso"n""['size_differen'c''e']} bytes larg'e''r",
              " "" "recommended_acti"o""n"":"" "Databases database appears to have more da"t""a"
            })

        # Check modification times
        db1_time = datetime.fromisoformat(db1_analysi"s""["last_modifi"e""d"])
        db2_time = datetime.fromisoformat(db2_analysi"s""["last_modifi"e""d"])

        if db1_time > db2_time:
            compariso"n""["recommendatio"n""s"].append(]
            })
        else:
            compariso"n""["recommendatio"n""s"].append(]
            })

    return comparison


def generate_enterprise_recommendation(comparison):
  " "" """Generate enterprise-compliant recommendati"o""n"""
    recommendation = {
      " "" "timesta"m""p": datetime.now().isoformat(),
      " "" "analysis_summa"r""y": {]
          " "" "identical_fil"e""s": compariso"n""["identical_fil"e""s"],
          " "" "size_differen"c""e": compariso"n""["size_differen"c""e"],
          " "" "both_accessib"l""e": True
        },
      " "" "enterprise_complian"c""e": {},
      " "" "recommended_actio"n""s": [],
      " "" "risk_assessme"n""t"":"" "L"O""W",
      " "" "implementation_ste"p""s": []
    }

    if compariso"n""["identical_fil"e""s"]:
        recommendatio"n""["recommended_actio"n""s"] = [
              " "" "comma"n""d"":"" "c"p"" 'E:/gh_COPILOT/production.'d''b''' 'E:/gh_COPILOT/databases/production_backup_$(date +%Y%m%d_%H%M%S).'d''b'"
            },
            {},
            {}
        ]
        recommendatio"n""["risk_assessme"n""t"] "="" "MINIM"A""L"
    else:
        # Files are different - need more careful analysis
        root_size = compariso"n""["file_comparis"o""n""]""["d"b""1""]""["si"z""e"]
        db_size = compariso"n""["file_comparis"o""n""]""["d"b""2""]""["si"z""e"]

        if root_size > db_size:
            recommendatio"n""["recommended_actio"n""s"] = [
                },
                {},
                {}
            ]
            recommendatio"n""["risk_assessme"n""t"] "="" "MEDI"U""M"
        else:
            recommendatio"n""["recommended_actio"n""s"] = [
                },
                {},
                {}
            ]
            recommendatio"n""["risk_assessme"n""t"] "="" "L"O""W"

    return recommendation


def main():
  " "" """Main analysis functi"o""n"""
    prin"t""("[SEARCH] PRODUCTION DATABASE ANALYSIS INITIAT"E""D")
    prin"t""("""=" * 60)

    # Define database paths
    root_db = Pat"h""("E:/gh_COPILOT/production."d""b")
    databases_db = Pat"h""("E:/gh_COPILOT/databases/production."d""b")

    # Check if both files exist
    if not root_db.exists():
        print"(""f"[ERROR] Root database not found: {root_d"b""}")
        return

    if not databases_db.exists():
        print"(""f"[ERROR] Databases database not found: {databases_d"b""}")
        return

    print"(""f"[SUCCESS] Both database files fou"n""d")
    print"(""f"[FOLDER] Root: {root_d"b""}")
    print"(""f"[FOLDER] Databases: {databases_d"b""}")
    print()

    # Analyze both databases
    prin"t""("[SEARCH] Analyzing root database."."".")
    root_analysis = analyze_database_structure(root_db)

    prin"t""("[SEARCH] Analyzing databases database."."".")
    databases_analysis = analyze_database_structure(databases_db)

    # Compare databases
    prin"t""("[SEARCH] Comparing databases."."".")
    comparison = compare_databases(root_analysis, databases_analysis)

    # Generate recommendation
    prin"t""("[SEARCH] Generating enterprise recommendation."."".")
    recommendation = generate_enterprise_recommendation(comparison)

    # Save results
    timestamp = datetime.now().strftim"e""("%Y%m%d_%H%M"%""S")

    # Save detailed analysis
    analysis_file =" ""f"E:/gh_COPILOT/production_db_analysis_{timestamp}.js"o""n"
    with open(analysis_file","" '''w') as f:
        json.dump(]
        }, f, indent=2)

    # Print summary
    prin't''("""\n" "+"" """=" * 60)
    prin"t""("[BAR_CHART] ANALYSIS SUMMA"R""Y")
    prin"t""("""=" * 60)
    print"(""f"Root Database Size: {root_analysi"s""['file_si'z''e']:,} byt'e''s")
    print(
       " ""f"Databases Database Size: {databases_analysi"s""['file_si'z''e']:,} byt'e''s")
    print"(""f"Size Difference: {compariso"n""['size_differen'c''e']:,} byt'e''s")
    print"(""f"Files Identical: {compariso"n""['identical_fil'e''s'']''}")
    print"(""f"Risk Assessment: {recommendatio"n""['risk_assessme'n''t'']''}")
    print()

    prin"t""("[CLIPBOARD] RECOMMENDED ACTION"S"":")
    for action in recommendatio"n""["recommended_actio"n""s"]:
        print(
           " ""f"  {actio"n""['priori't''y']}. {actio'n''['acti'o''n']}: {actio'n''['descripti'o''n'']''}")

    print"(""f"\n[STORAGE] Detailed analysis saved to: {analysis_fil"e""}")
    prin"t""("[SUCCESS] PRODUCTION DATABASE ANALYSIS COMPLE"T""E")


if __name__ ="="" "__main"_""_":
    main()"
""