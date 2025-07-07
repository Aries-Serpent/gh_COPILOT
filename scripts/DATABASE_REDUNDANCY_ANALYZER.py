#!/usr/bin/env python3
"""
ENTERPRISE DATABASE REDUNDANCY ANALYSIS
=======================================

This script validates database files in staging directory to identify
redundant or duplicate files that may no longer be needed after our 
complete database capture.

COMPLIANCE: Enterprise data management and storage optimization
"""

import os
import hashlib
import json
from pathlib import Path
from datetime import datetime
import shutil

class DatabaseRedundancyAnalyzer:
    def __init__(self):
        self.staging_db_path = Path('E:/gh_COPILOT/databases')
        self.local_db_path = Path('databases')
        self.analysis_results = {
            "analysis_timestamp": datetime.now().isoformat(),
            "staging_analysis": {},
            "local_analysis": {},
            "comparison_results": {},
            "recommendations": [],
            "redundant_files": [],
            "safe_to_remove": []
        }
        
    def analyze_directory(self, directory_path: Path, label: str) -> dict:
        """Analyze a directory for database files"""
        print(f"[SEARCH] Analyzing {label}: {directory_path}")
        
        if not directory_path.exists():
            print(f"[ERROR] Directory not found: {directory_path}")
            return {
                "exists": False,
                "total_files": 0,
                "file_types": {},
                "files_by_name": {},
                "total_size": 0
            }
        
        files = list(directory_path.glob('**/*'))
        file_list = [f for f in files if f.is_file()]
        
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
                    "path": str(file),
                    "size": file.stat().st_size,
                    "modified": datetime.fromtimestamp(file.stat().st_mtime).isoformat(),
                    "hash": self._calculate_file_hash(file) if file.stat().st_size < 10*1024*1024 else "TOO_LARGE"
                }
                
                files_by_name[file.name] = file_info
                total_size += file_info["size"]
        
        result = {
            "exists": True,
            "total_files": len(file_list),
            "file_types": file_types,
            "files_by_name": files_by_name,
            "total_size": total_size,
            "total_size_mb": total_size / (1024*1024)
        }
        
        print(f"[SUCCESS] {label} analysis complete:")
        print(f"   - Total files: {result['total_files']}")
        print(f"   - Total size: {result['total_size_mb']:.2f} MB")
        print(f"   - File types: {dict(sorted(file_types.items()))}")
        
        return result
        
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of a file"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception as e:
            return f"ERROR: {str(e)}"
    
    def compare_directories(self) -> dict:
        """Compare staging and local directories for redundancy"""
        print("\n[SEARCH] COMPARING DIRECTORIES FOR REDUNDANCY")
        print("-" * 45)
        
        staging_analysis = self.analysis_results["staging_analysis"]
        local_analysis = self.analysis_results["local_analysis"]
        
        if not staging_analysis["exists"] or not local_analysis["exists"]:
            print("[ERROR] Cannot compare - one or both directories don't exist")
            return {
                "can_compare": False,
                "common_files": [],
                "identical_files": [],
                "staging_only": [],
                "local_only": [],
                "potential_duplicates": []
            }
        
        staging_files = staging_analysis["files_by_name"]
        local_files = local_analysis["files_by_name"]
        
        # Find common file names
        common_names = set(staging_files.keys()) & set(local_files.keys())
        staging_only = set(staging_files.keys()) - set(local_files.keys())
        local_only = set(local_files.keys()) - set(staging_files.keys())
        
        # Find identical files (same hash)
        identical_files = []
        potential_duplicates = []
        
        for name in common_names:
            staging_file = staging_files[name]
            local_file = local_files[name]
            
            if staging_file["hash"] == local_file["hash"] and staging_file["hash"] != "TOO_LARGE":
                identical_files.append({
                    "name": name,
                    "staging_path": staging_file["path"],
                    "local_path": local_file["path"],
                    "size": staging_file["size"],
                    "hash": staging_file["hash"]
                })
            else:
                potential_duplicates.append({
                    "name": name,
                    "staging_info": staging_file,
                    "local_info": local_file
                })
        
        comparison_results = {
            "can_compare": True,
            "common_files": list(common_names),
            "identical_files": identical_files,
            "staging_only": list(staging_only),
            "local_only": list(local_only),
            "potential_duplicates": potential_duplicates
        }
        
        print(f"[BAR_CHART] Comparison Results:")
        print(f"   - Common file names: {len(common_names)}")
        print(f"   - Identical files: {len(identical_files)}")
        print(f"   - Staging-only files: {len(staging_only)}")
        print(f"   - Local-only files: {len(local_only)}")
        print(f"   - Potential duplicates: {len(potential_duplicates)}")
        
        return comparison_results
    
    def generate_recommendations(self) -> list:
        """Generate recommendations for file cleanup"""
        print("\n[TARGET] GENERATING RECOMMENDATIONS")
        print("-" * 30)
        
        recommendations = []
        comparison = self.analysis_results["comparison_results"]
        
        if not comparison["can_compare"]:
            recommendations.append("Cannot analyze - staging or local directory missing")
            return recommendations
        
        # Recommend removal of identical files from staging
        if comparison["identical_files"]:
            recommendations.append(f"SAFE TO REMOVE: {len(comparison['identical_files'])} identical files from staging")
            for file in comparison["identical_files"]:
                self.analysis_results["safe_to_remove"].append(file["staging_path"])
        
        # Analyze staging-only files
        if comparison["staging_only"]:
            recommendations.append(f"REVIEW NEEDED: {len(comparison['staging_only'])} staging-only files")
            
            # Check if staging-only files are old variants
            staging_analysis = self.analysis_results["staging_analysis"]
            for file_name in comparison["staging_only"]:
                file_info = staging_analysis["files_by_name"][file_name]
                modified_date = datetime.fromisoformat(file_info["modified"])
                days_old = (datetime.now() - modified_date).days
                
                if days_old > 7:  # Consider files older than 7 days as potential cleanup candidates
                    recommendations.append(f"CANDIDATE FOR REMOVAL: {file_name} (age: {days_old} days)")
                    self.analysis_results["redundant_files"].append(file_info["path"])
        
        # Check for database completeness
        local_analysis = self.analysis_results["local_analysis"]
        if local_analysis["exists"] and local_analysis["total_files"] > 0:
            recommendations.append("[SUCCESS] Local database appears complete - staging files may be redundant")
        
        # Storage optimization
        staging_size = self.analysis_results["staging_analysis"].get("total_size_mb", 0)
        if staging_size > 50:  # If staging is > 50MB
            recommendations.append(f"STORAGE OPTIMIZATION: Staging directory uses {staging_size:.2f} MB")
        
        return recommendations
    
    def create_cleanup_plan(self) -> dict:
        """Create a detailed cleanup plan"""
        print("\n[CLIPBOARD] CREATING CLEANUP PLAN")
        print("-" * 25)
        
        cleanup_plan = {
            "total_files_to_remove": len(self.analysis_results["safe_to_remove"]) + len(self.analysis_results["redundant_files"]),
            "safe_removals": self.analysis_results["safe_to_remove"],
            "redundant_removals": self.analysis_results["redundant_files"],
            "space_savings_mb": 0,
            "backup_required": True,
            "cleanup_script": self._generate_cleanup_script()
        }
        
        # Calculate space savings
        staging_analysis = self.analysis_results["staging_analysis"]
        if staging_analysis["exists"]:
            for file_path in cleanup_plan["safe_removals"] + cleanup_plan["redundant_removals"]:
                file_name = Path(file_path).name
                if file_name in staging_analysis["files_by_name"]:
                    cleanup_plan["space_savings_mb"] += staging_analysis["files_by_name"][file_name]["size"] / (1024*1024)
        
        print(f"[BAR_CHART] Cleanup Plan Summary:")
        print(f"   - Files to remove: {cleanup_plan['total_files_to_remove']}")
        print(f"   - Space savings: {cleanup_plan['space_savings_mb']:.2f} MB")
        print(f"   - Backup required: {cleanup_plan['backup_required']}")
        
        return cleanup_plan
    
    def _generate_cleanup_script(self) -> str:
        """Generate a cleanup script"""
        script_lines = [
            "#!/usr/bin/env python3",
            '"""Generated cleanup script for staging database files"""',
            "",
            "import os",
            "import shutil",
            "from pathlib import Path",
            "from datetime import datetime",
            "",
            "# Create backup before cleanup",
            "backup_dir = f'staging_db_backup_{int(datetime.now().timestamp())}'",
            "shutil.copytree('E:/gh_COPILOT/databases', backup_dir)",
            "print(f'[SUCCESS] Backup created: {backup_dir}')",
            "",
            "# Files to remove (identical to local database)",
            "safe_removals = ["
        ]
        
        for file_path in self.analysis_results["safe_to_remove"]:
            script_lines.append(f'    "{file_path}",')
        
        script_lines.extend([
            "]",
            "",
            "# Remove safe files",
            "for file_path in safe_removals:",
            "    try:",
            "        os.remove(file_path)",
            "        print(f'[SUCCESS] Removed: {file_path}')",
            "    except Exception as e:",
            "        print(f'[ERROR] Error removing {file_path}: {e}')",
            "",
            "print('[COMPLETE] Cleanup completed!')"
        ])
        
        return "\n".join(script_lines)
    
    def execute_full_analysis(self) -> dict:
        """Execute complete redundancy analysis"""
        print("[LAUNCH] ENTERPRISE DATABASE REDUNDANCY ANALYSIS")
        print("=" * 60)
        
        # Analyze staging directory
        self.analysis_results["staging_analysis"] = self.analyze_directory(
            self.staging_db_path, "Staging Database"
        )
        
        # Analyze local directory
        self.analysis_results["local_analysis"] = self.analyze_directory(
            self.local_db_path, "Local Database"
        )
        
        # Compare directories
        self.analysis_results["comparison_results"] = self.compare_directories()
        
        # Generate recommendations
        self.analysis_results["recommendations"] = self.generate_recommendations()
        
        # Create cleanup plan
        self.analysis_results["cleanup_plan"] = self.create_cleanup_plan()
        
        # Save analysis report
        report_path = f"DATABASE_REDUNDANCY_ANALYSIS_{int(datetime.now().timestamp())}.json"
        with open(report_path, 'w') as f:
            json.dump(self.analysis_results, f, indent=2)
        
        print(f"\n[?] Analysis report saved: {report_path}")
        
        return self.analysis_results

def main():
    """Main execution function"""
    print("[?] ENTERPRISE DATABASE REDUNDANCY ANALYZER")
    print("[?] OPTIMIZING STORAGE AND ELIMINATING DUPLICATES")
    print()
    
    analyzer = DatabaseRedundancyAnalyzer()
    results = analyzer.execute_full_analysis()
    
    print("\n" + "=" * 60)
    print("[SUCCESS] ANALYSIS COMPLETE")
    print(f"[BAR_CHART] Total recommendations: {len(results['recommendations'])}")
    print(f"[BAR_CHART] Files safe to remove: {len(results['safe_to_remove'])}")
    print(f"[BAR_CHART] Redundant files identified: {len(results['redundant_files'])}")
    
    if results['recommendations']:
        print("\n[TARGET] KEY RECOMMENDATIONS:")
        for rec in results['recommendations']:
            print(f"   - {rec}")
    
    return results

if __name__ == "__main__":
    main()
