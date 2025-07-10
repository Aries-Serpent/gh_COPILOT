#!/usr/bin/env python3
"""
ENTERPRISE DATABASE REDUNDANCY ANALYSIS
=======================================

This script validates database files in staging directory to identify
redundant or duplicate files that may no longer be needed after our
complete database capture.

COMPLIANCE: Enterprise data management and storage optimizatio"n""
"""

import os
import hashlib
import json
from pathlib import Path
from datetime import datetime
import shutil


class DatabaseRedundancyAnalyzer:
    def __init__(self):
        self.staging_db_path = Pat"h""('E:/gh_COPILOT/databas'e''s')
        self.local_db_path = Pat'h''('databas'e''s')
        self.analysis_results = {
          ' '' "analysis_timesta"m""p": datetime.now().isoformat(),
          " "" "staging_analys"i""s": {},
          " "" "local_analys"i""s": {},
          " "" "comparison_resul"t""s": {},
          " "" "recommendatio"n""s": [],
          " "" "redundant_fil"e""s": [],
          " "" "safe_to_remo"v""e": []
        }

    def analyze_directory(self, directory_path: Path, label: str) -> dict:
      " "" """Analyze a directory for database fil"e""s"""
        print"(""f"[SEARCH] Analyzing {label}: {directory_pat"h""}")

        if not directory_path.exists():
            print"(""f"[ERROR] Directory not found: {directory_pat"h""}")
            return {]
              " "" "file_typ"e""s": {},
              " "" "files_by_na"m""e": {},
              " "" "total_si"z""e": 0
            }

        files = list(directory_path.glo"b""('**'/''*'))
        file_list = [
    f for f in files if f.is_file(
]]

        # Analyze file types
        file_types = {}
        files_by_name = {}
        total_size = 0

        for file in file_list:
            if file.is_file():
                ext = file.suffix.lower()
                file_types[ext] = file_types.get(ext, 0) + 1

                # Get file info
                file_info = {
                  ' '' "pa"t""h": str(file),
                  " "" "si"z""e": file.stat().st_size,
                  " "" "modifi"e""d": datetime.fromtimestamp(file.stat().st_mtime).isoformat(),
                  " "" "ha"s""h": self._calculate_file_hash(file) if file.stat().st_size < 10 * 1024 * 1024 els"e"" "TOO_LAR"G""E"
                }

                files_by_name[file.name] = file_info
                total_size += file_inf"o""["si"z""e"]

        result = {
          " "" "total_fil"e""s": len(file_list),
          " "" "file_typ"e""s": file_types,
          " "" "files_by_na"m""e": files_by_name,
          " "" "total_si"z""e": total_size,
          " "" "total_size_"m""b": total_size / (1024 * 1024)
        }

        print"(""f"[SUCCESS] {label} analysis complet"e"":")
        print"(""f"   - Total files: {resul"t""['total_fil'e''s'']''}")
        print"(""f"   - Total size: {resul"t""['total_size_'m''b']:.2f} 'M''B")
        print"(""f"   - File types: {dict(sorted(file_types.items())")""}")

        return result

    def _calculate_file_hash(self, file_path: Path) -> str:
      " "" """Calculate SHA-256 hash of a fi"l""e"""
        try:
            with open(file_path","" ''r''b') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception as e:
            return' ''f"ERROR: {str(e")""}"
    def compare_directories(self) -> dict:
      " "" """Compare staging and local directories for redundan"c""y"""
        prin"t""("\n[SEARCH] COMPARING DIRECTORIES FOR REDUNDAN"C""Y")
        prin"t""("""-" * 45)

        staging_analysis = self.analysis_result"s""["staging_analys"i""s"]
        local_analysis = self.analysis_result"s""["local_analys"i""s"]

        if not staging_analysi"s""["exis"t""s"] or not local_analysi"s""["exis"t""s"]:
            prin"t""("[ERROR] Cannot compare - one or both directories d"o""n't exi's''t")
            return {]
              " "" "common_fil"e""s": [],
              " "" "identical_fil"e""s": [],
              " "" "staging_on"l""y": [],
              " "" "local_on"l""y": [],
              " "" "potential_duplicat"e""s": []
            }

        staging_files = staging_analysi"s""["files_by_na"m""e"]
        local_files = local_analysi"s""["files_by_na"m""e"]

        # Find common file names
        common_names = set(staging_files.keys()) & set(local_files.keys())
        staging_only = set(staging_files.keys()) - set(local_files.keys())
        local_only = set(local_files.keys()) - set(staging_files.keys())

        # Find identical files (same hash)
        identical_files = [
        potential_duplicates = [

        for name in common_names:
            staging_file = staging_files[name]
            local_file = local_files[name]

            if staging_fil"e""["ha"s""h"] == local_fil"e""["ha"s""h"] and staging_fil"e""["ha"s""h"] !"="" "TOO_LAR"G""E":
                identical_files.append(]
                  " "" "staging_pa"t""h": staging_fil"e""["pa"t""h"],
                  " "" "local_pa"t""h": local_fil"e""["pa"t""h"],
                  " "" "si"z""e": staging_fil"e""["si"z""e"],
                  " "" "ha"s""h": staging_fil"e""["ha"s""h"]
                })
            else:
                potential_duplicates.append(]
                })

        comparison_results = {
          " "" "common_fil"e""s": list(common_names),
          " "" "identical_fil"e""s": identical_files,
          " "" "staging_on"l""y": list(staging_only),
          " "" "local_on"l""y": list(local_only),
          " "" "potential_duplicat"e""s": potential_duplicates
        }

        print"(""f"[BAR_CHART] Comparison Result"s"":")
        print"(""f"   - Common file names: {len(common_names")""}")
        print"(""f"   - Identical files: {len(identical_files")""}")
        print"(""f"   - Staging-only files: {len(staging_only")""}")
        print"(""f"   - Local-only files: {len(local_only")""}")
        print"(""f"   - Potential duplicates: {len(potential_duplicates")""}")

        return comparison_results

    def generate_recommendations(self) -> list:
      " "" """Generate recommendations for file clean"u""p"""
        prin"t""("\n[TARGET] GENERATING RECOMMENDATIO"N""S")
        prin"t""("""-" * 30)

        recommendations = [
        comparison = self.analysis_result"s""["comparison_resul"t""s"]

        if not compariso"n""["can_compa"r""e"]:
            recommendations.append(]
              " "" "Cannot analyze - staging or local directory missi"n""g")
            return recommendations

        # Recommend removal of identical files from staging
        if compariso"n""["identical_fil"e""s"]:
            recommendations.append(]
               " ""f"SAFE TO REMOVE: {len(compariso"n""['identical_fil'e''s'])} identical files from stagi'n''g")
            for file in compariso"n""["identical_fil"e""s"]:
                self.analysis_result"s""["safe_to_remo"v""e"].append(]
                    fil"e""["staging_pa"t""h"])

        # Analyze staging-only files
        if compariso"n""["staging_on"l""y"]:
            recommendations.append(]
               " ""f"REVIEW NEEDED: {len(compariso"n""['staging_on'l''y'])} staging-only fil'e''s")

            # Check if staging-only files are old variants
            staging_analysis = self.analysis_result"s""["staging_analys"i""s"]
            for file_name in compariso"n""["staging_on"l""y"]:
                file_info = staging_analysi"s""["files_by_na"m""e"][file_name]
                modified_date = datetime.fromisoformat(file_inf"o""["modifi"e""d"])
                days_old = (datetime.now() - modified_date).days

                if days_old > 7:  # Consider files older than 7 days as potential cleanup candidates
                    recommendations.append(]
                       " ""f"CANDIDATE FOR REMOVAL: {file_name} (age: {days_old} day"s"")")
                    self.analysis_result"s""["redundant_fil"e""s"].append(]
                        file_inf"o""["pa"t""h"])

        # Check for database completeness
        local_analysis = self.analysis_result"s""["local_analys"i""s"]
        if local_analysi"s""["exis"t""s"] and local_analysi"s""["total_fil"e""s"] > 0:
            recommendations.append(]
              " "" "[SUCCESS] Local database appears complete - staging files may be redunda"n""t")

        # Storage optimization
        staging_size = self.analysis_result"s""["staging_analys"i""s"].get(]
          " "" "total_size_"m""b", 0)
        if staging_size > 50:  # If staging is > 50MB
            recommendations.append(]
               " ""f"STORAGE OPTIMIZATION: Staging directory uses {staging_size:.2f} "M""B")

        return recommendations

    def create_cleanup_plan(self) -> dict:
      " "" """Create a detailed cleanup pl"a""n"""
        prin"t""("\n[CLIPBOARD] CREATING CLEANUP PL"A""N")
        prin"t""("""-" * 25)

        cleanup_plan = {
          " "" "total_files_to_remo"v""e": len(self.analysis_result"s""["safe_to_remo"v""e"]) + len(self.analysis_result"s""["redundant_fil"e""s"]),
          " "" "safe_remova"l""s": self.analysis_result"s""["safe_to_remo"v""e"],
          " "" "redundant_remova"l""s": self.analysis_result"s""["redundant_fil"e""s"],
          " "" "space_savings_"m""b": 0,
          " "" "backup_requir"e""d": True,
          " "" "cleanup_scri"p""t": self._generate_cleanup_script()
        }

        # Calculate space savings
        staging_analysis = self.analysis_result"s""["staging_analys"i""s"]
        if staging_analysi"s""["exis"t""s"]:
            for file_path in cleanup_pla"n""["safe_remova"l""s"]
                + cleanup_pla"n""["redundant_remova"l""s"]:
                file_name = Path(file_path).name
                if file_name in staging_analysi"s""["files_by_na"m""e"]:
                    cleanup_pla"n""["space_savings_"m""b"] += staging_analysi"s""["files_by_na"m""e"][file_name"]""["si"z""e"] / (]
                        1024 * 1024)

        print"(""f"[BAR_CHART] Cleanup Plan Summar"y"":")
        print"(""f"   - Files to remove: {cleanup_pla"n""['total_files_to_remo'v''e'']''}")
        print"(""f"   - Space savings: {cleanup_pla"n""['space_savings_'m''b']:.2f} 'M''B")
        print"(""f"   - Backup required: {cleanup_pla"n""['backup_requir'e''d'']''}")

        return cleanup_plan

    def _generate_cleanup_script(self) -> str:
      " "" """Generate a cleanup scri"p""t"""
        script_lines = [
  " "" "backup_dir =" ""f'staging_db_backup_{int(datetime.now(
].timestamp()')''}'",
          " "" "shutil.copytre"e""('E:/gh_COPILOT/databas'e''s', backup_di'r'')",
          " "" "print"(""f'[SUCCESS] Backup created: {backup_di'r''}''')",
          " "" "",
          " "" "# Files to remove (identical to local databas"e"")",
          " "" "safe_removals = [
        ]

        for file_path in self.analysis_result"s""["safe_to_remo"v""e"]:
            script_lines.append"(""f'  ' '' "{file_pat"h""}""",')

        script_lines.extend(]
          ' '' """]",
          " "" "",
          " "" "# Remove safe fil"e""s",
          " "" "for file_path in safe_removal"s"":",
          " "" "    tr"y"":",
          " "" "        os.remove(file_pat"h"")",
          " "" "        print"(""f'[SUCCESS] Removed: {file_pat'h''}''')",
          " "" "    except Exception as "e"":",
          " "" "        print"(""f'[ERROR] Error removing {file_path}: {'e''}''')",
          " "" "",
          " "" "prin"t""('[COMPLETE] Cleanup complete'd''!''')"
        ])

        retur"n"" """\n".join(script_lines)

    def execute_full_analysis(self) -> dict:
      " "" """Execute complete redundancy analys"i""s"""
        prin"t""("[LAUNCH] ENTERPRISE DATABASE REDUNDANCY ANALYS"I""S")
        prin"t""("""=" * 60)

        # Analyze staging directory
        self.analysis_result"s""["staging_analys"i""s"] = self.analyze_directory(]
        )

        # Analyze local directory
        self.analysis_result"s""["local_analys"i""s"] = self.analyze_directory(]
        )

        # Compare directories
        self.analysis_result"s""["comparison_resul"t""s"] = self.compare_directories(]
        )

        # Generate recommendations
        self.analysis_result"s""["recommendatio"n""s"] = self.generate_recommendations(]
        )

        # Create cleanup plan
        self.analysis_result"s""["cleanup_pl"a""n"] = self.create_cleanup_plan()

        # Save analysis report
        report_path =" ""f"DATABASE_REDUNDANCY_ANALYSIS_{int(datetime.now().timestamp())}.js"o""n"
        with open(report_path","" '''w') as f:
            json.dump(self.analysis_results, f, indent=2)

        print'(''f"\n[?] Analysis report saved: {report_pat"h""}")

        return self.analysis_results


def main():
  " "" """Main execution functi"o""n"""
    prin"t""("[?] ENTERPRISE DATABASE REDUNDANCY ANALYZ"E""R")
    prin"t""("[?] OPTIMIZING STORAGE AND ELIMINATING DUPLICAT"E""S")
    print()

    analyzer = DatabaseRedundancyAnalyzer()
    results = analyzer.execute_full_analysis()

    prin"t""("""\n" "+"" """=" * 60)
    prin"t""("[SUCCESS] ANALYSIS COMPLE"T""E")
    print(
       " ""f"[BAR_CHART] Total recommendations: {len(result"s""['recommendatio'n''s']')''}")
    print(
       " ""f"[BAR_CHART] Files safe to remove: {len(result"s""['safe_to_remo'v''e']')''}")
    print(
       " ""f"[BAR_CHART] Redundant files identified: {len(result"s""['redundant_fil'e''s']')''}")

    if result"s""['recommendatio'n''s']:
        prin't''("\n[TARGET] KEY RECOMMENDATION"S"":")
        for rec in result"s""['recommendatio'n''s']:
            print'(''f"   - {re"c""}")

    return results


if __name__ ="="" "__main"_""_":
    main()"
""