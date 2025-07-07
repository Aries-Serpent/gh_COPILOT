#!/usr/bin/env python3
"""
Production Database Comprehensive Script Analysis
Determines:
1. Which scripts are stored in production.db vs filesystem
2. Database's capability for environment-adaptive script generation
"""

import sqlite3
import os
import json
import hashlib
from datetime import datetime
from pathlib import Path
import difflib

class ProductionDBScriptAnalyzer:
    def __init__(self, workspace_path):
        self.workspace_path = Path(workspace_path)
        self.db_path = self.workspace_path / "databases" / "production.db"
        self.results = {
            "analysis_timestamp": datetime.now().isoformat(),
            "workspace_path": str(workspace_path),
            "filesystem_scripts": {},
            "database_scripts": {},
            "script_comparison": {},
            "environment_adaptation": {},
            "adaptive_generation_capability": {},
            "recommendations": []
        }
        
    def scan_filesystem_scripts(self):
        """Scan all Python scripts in the workspace"""
        print("Scanning filesystem for Python scripts...")
        
        scripts = {}
        for py_file in self.workspace_path.rglob("*.py"):
            try:
                # Skip backup directories and __pycache__
                if any(part.startswith(('_backup', '__pycache__', '.git')) for part in py_file.parts):
                    continue
                    
                relative_path = py_file.relative_to(self.workspace_path)
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Calculate hash for comparison
                content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
                
                scripts[str(relative_path)] = {
                    "full_path": str(py_file),
                    "size_bytes": py_file.stat().st_size,
                    "content_hash": content_hash,
                    "line_count": len(content.splitlines()),
                    "modified_time": datetime.fromtimestamp(py_file.stat().st_mtime).isoformat(),
                    "contains_framework_logic": self._analyze_framework_content(content)
                }
                
            except Exception as e:
                print(f"Error processing {py_file}: {e}")
                
        self.results["filesystem_scripts"] = scripts
        print(f"Found {len(scripts)} Python scripts in filesystem")
        return scripts
    
    def analyze_database_scripts(self):
        """Analyze scripts stored in production.db"""
        print("Analyzing scripts stored in production.db...")
        
        if not self.db_path.exists():
            print("ERROR: production.db not found!")
            return {}
            
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Check file_system_mapping table
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='file_system_mapping'")
            if not cursor.fetchone():
                print("No file_system_mapping table found")
                return {}
            
            # Get all scripts from database (using correct column names)
            cursor.execute("""
                SELECT file_path, file_content, file_hash, file_size, created_at, updated_at,
                       status, file_type, backup_location, compression_type, encoding
                FROM file_system_mapping 
                WHERE file_path LIKE '%.py'
                ORDER BY file_path
            """)
            
            db_scripts = {}
            for row in cursor.fetchall():
                file_path, file_content, file_hash, file_size, created_at, updated_at, status, file_type, backup_location, compression_type, encoding = row
                
                if file_content:
                    db_scripts[file_path] = {
                        "content_length": len(file_content),
                        "content_hash": file_hash or hashlib.md5(file_content.encode('utf-8')).hexdigest(),
                        "file_size": file_size,
                        "created_at": created_at,
                        "updated_at": updated_at,
                        "status": status,
                        "file_type": file_type,
                        "backup_location": backup_location,
                        "compression_type": compression_type,
                        "encoding": encoding,
                        "has_content": True,
                        "framework_elements": self._analyze_framework_content(file_content)
                    }
                else:
                    db_scripts[file_path] = {
                        "content_length": 0,
                        "has_content": False,
                        "file_size": file_size or 0,
                        "created_at": created_at,
                        "updated_at": updated_at,
                        "status": status,
                        "file_type": file_type
                    }
            
            conn.close()
            self.results["database_scripts"] = db_scripts
            print(f"Found {len(db_scripts)} Python scripts in database")
            return db_scripts
            
        except Exception as e:
            print(f"Error analyzing database scripts: {e}")
            return {}
    
    def analyze_environment_adaptation(self):
        """Analyze database's environment adaptation capabilities"""
        print("Analyzing environment adaptation capabilities...")
        
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Check for environment-related tables and columns
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            env_capabilities = {
                "environment_tables": [],
                "adaptive_columns": {},
                "template_storage": False,
                "version_tracking": False,
                "deployment_configs": False
            }
            
            # Check each table for environment-related columns
            for table in tables:
                cursor.execute(f"PRAGMA table_info({table})")
                columns = cursor.fetchall()
                
                env_columns = []
                for col in columns:
                    col_name = col[1].lower()
                    if any(keyword in col_name for keyword in ['environment', 'deploy', 'config', 'context', 'adaptive', 'template']):
                        env_columns.append(col[1])
                
                if env_columns:
                    env_capabilities["adaptive_columns"][table] = env_columns
                    
                # Check for specific capabilities
                if table.lower() in ['environment_configs', 'deployment_environments']:
                    env_capabilities["environment_tables"].append(table)
                    
                if any('template' in col[1].lower() for col in columns):
                    env_capabilities["template_storage"] = True
                    
                if any('version' in col[1].lower() for col in columns):
                    env_capabilities["version_tracking"] = True
                    
                if any('deploy' in col[1].lower() for col in columns):
                    env_capabilities["deployment_configs"] = True
            
            # Check for script generation patterns (using correct column names)
            cursor.execute("""
                SELECT COUNT(*) FROM file_system_mapping 
                WHERE file_content IS NOT NULL AND file_content != ''
            """)
            content_scripts = cursor.fetchone()[0]
            env_capabilities["content_stored_scripts"] = content_scripts
            
            # Check for template patterns in stored content
            cursor.execute("""
                SELECT COUNT(*) FROM file_system_mapping 
                WHERE file_content LIKE '%{{%}}%' OR file_content LIKE '%${%}%'
            """)
            template_scripts = cursor.fetchone()[0]
            env_capabilities["template_patterns"] = template_scripts
            
            conn.close()
            self.results["environment_adaptation"] = env_capabilities
            return env_capabilities
            
        except Exception as e:
            print(f"Error analyzing environment adaptation: {e}")
            return {}
    
    def analyze_adaptive_generation_capability(self):
        """Analyze database's capability for adaptive script generation"""
        print("Analyzing adaptive script generation capability...")
        
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            capabilities = {
                "script_templates": 0,
                "environment_variants": 0,
                "generation_metadata": False,
                "dynamic_content": False,
                "parameter_substitution": False,
                "deployment_automation": False,
                "adaptive_patterns": []
            }
            
            # Check for script templates and variants (using correct column names)
            cursor.execute("""
                SELECT file_path, file_content, backup_location, status
                FROM file_system_mapping 
                WHERE file_content IS NOT NULL
            """)
            
            for row in cursor.fetchall():
                file_path, file_content, backup_location, status = row
                
                # Check for template patterns
                if file_content and ('{{' in file_content or '${' in file_content or '%s' in file_content):
                    capabilities["script_templates"] += 1
                    capabilities["parameter_substitution"] = True
                
                # Check for environment variants based on backup location or status
                if backup_location or status != 'active':
                    capabilities["environment_variants"] += 1
                    
                # Check for deployment automation based on backup patterns
                if backup_location and 'deploy' in backup_location.lower():
                    capabilities["deployment_automation"] = True
                    
                # Check for dynamic content patterns
                if file_content and any(pattern in file_content for pattern in ['import os', 'sys.platform', 'environment', 'config']):
                    capabilities["dynamic_content"] = True
            
            # Check for generation metadata in tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            generation_tables = [t for t in tables if any(keyword in t.lower() for keyword in ['generation', 'template', 'pattern'])]
            if generation_tables:
                capabilities["generation_metadata"] = True
                capabilities["adaptive_patterns"] = generation_tables
            
            # Check for script generation functions or procedures (using correct column name)
            cursor.execute("""
                SELECT file_content FROM file_system_mapping 
                WHERE file_content LIKE '%def generate_%' OR file_content LIKE '%def create_script%'
            """)
            generation_functions = cursor.fetchall()
            capabilities["generation_functions"] = len(generation_functions)
            
            conn.close()
            self.results["adaptive_generation_capability"] = capabilities
            return capabilities
            
        except Exception as e:
            print(f"Error analyzing adaptive generation capability: {e}")
            return {}
    
    def compare_scripts(self):
        """Compare scripts between filesystem and database"""
        print("Comparing scripts between filesystem and database...")
        
        fs_scripts = self.results.get("filesystem_scripts", {})
        db_scripts = self.results.get("database_scripts", {})
        
        comparison = {
            "total_filesystem": len(fs_scripts),
            "total_database": len(db_scripts),
            "in_both": 0,
            "only_filesystem": 0,
            "only_database": 0,
            "content_matches": 0,
            "content_differs": 0,
            "detailed_comparison": {}
        }
        
        # Compare each filesystem script
        for fs_path, fs_data in fs_scripts.items():
            if fs_path in db_scripts:
                comparison["in_both"] += 1
                db_data = db_scripts[fs_path]
                
                if db_data.get("has_content", False):
                    if fs_data["content_hash"] == db_data.get("content_hash", ""):
                        comparison["content_matches"] += 1
                        match_status = "EXACT_MATCH"
                    else:
                        comparison["content_differs"] += 1
                        match_status = "CONTENT_DIFFERS"
                else:
                    match_status = "NO_DB_CONTENT"
                    
                comparison["detailed_comparison"][fs_path] = {
                    "status": match_status,
                    "filesystem_hash": fs_data["content_hash"],
                    "database_hash": db_data.get("content_hash", ""),
                    "filesystem_size": fs_data["size_bytes"],
                    "database_size": db_data.get("content_length", 0)
                }
            else:
                comparison["only_filesystem"] += 1
                comparison["detailed_comparison"][fs_path] = {
                    "status": "ONLY_FILESYSTEM",
                    "filesystem_hash": fs_data["content_hash"],
                    "filesystem_size": fs_data["size_bytes"]
                }
        
        # Check for database-only scripts
        for db_path in db_scripts:
            if db_path not in fs_scripts:
                comparison["only_database"] += 1
                comparison["detailed_comparison"][db_path] = {
                    "status": "ONLY_DATABASE",
                    "database_hash": db_scripts[db_path].get("content_hash", ""),
                    "database_size": db_scripts[db_path].get("content_length", 0)
                }
        
        self.results["script_comparison"] = comparison
        return comparison
    
    def _analyze_framework_content(self, content):
        """Analyze if content contains framework-specific logic"""
        framework_patterns = [
            "step1_factory_deployment",
            "step2_monitor_learning", 
            "step3_collect_analytics",
            "step4_performance_analysis",
            "step5_scale_capabilities",
            "step6_continuous_innovation",
            "master_framework_orchestrator",
            "scaling_innovation_framework",
            "DUAL_COPILOT",
            "anti_recursion",
            "enterprise_compliance"
        ]
        
        found_patterns = []
        for pattern in framework_patterns:
            if pattern in content:
                found_patterns.append(pattern)
                
        return found_patterns
    
    def generate_recommendations(self):
        """Generate recommendations based on analysis"""
        print("Generating recommendations...")
        
        recommendations = []
        
        comparison = self.results.get("script_comparison", {})
        env_adaptation = self.results.get("environment_adaptation", {})
        adaptive_gen = self.results.get("adaptive_generation_capability", {})
        
        # Script storage recommendations
        if comparison.get("only_filesystem", 0) > 0:
            recommendations.append({
                "type": "SCRIPT_STORAGE",
                "priority": "HIGH",
                "issue": f"{comparison['only_filesystem']} scripts exist only in filesystem",
                "recommendation": "Sync all framework scripts to production.db for centralized management"
            })
        
        if comparison.get("content_differs", 0) > 0:
            recommendations.append({
                "type": "CONTENT_SYNC",
                "priority": "MEDIUM", 
                "issue": f"{comparison['content_differs']} scripts have different content in database vs filesystem",
                "recommendation": "Update database with latest script versions or implement automated sync"
            })
        
        # Environment adaptation recommendations
        if not env_adaptation.get("template_storage", False):
            recommendations.append({
                "type": "TEMPLATE_SYSTEM",
                "priority": "HIGH",
                "issue": "No template storage system detected",
                "recommendation": "Implement script template storage for environment-adaptive generation"
            })
        
        if adaptive_gen.get("script_templates", 0) == 0:
            recommendations.append({
                "type": "ADAPTIVE_GENERATION",
                "priority": "HIGH", 
                "issue": "No parameterized script templates found",
                "recommendation": "Create environment-adaptive script templates with parameter substitution"
            })
        
        # Framework completeness
        fs_scripts = self.results.get("filesystem_scripts", {})
        framework_scripts = [path for path, data in fs_scripts.items() if data.get("contains_framework_logic")]
        
        if len(framework_scripts) < 8:  # Expected: 6 steps + orchestrator + scaling framework
            recommendations.append({
                "type": "FRAMEWORK_COMPLETENESS",
                "priority": "MEDIUM",
                "issue": f"Only {len(framework_scripts)} framework scripts detected",
                "recommendation": "Verify all 6-step framework components are present and properly stored"
            })
        
        self.results["recommendations"] = recommendations
        return recommendations
    
    def run_complete_analysis(self):
        """Run complete analysis and generate report"""
        print("Starting Production DB Comprehensive Script Analysis...")
        print("=" * 60)
        
        # Run all analysis phases
        self.scan_filesystem_scripts()
        print()
        
        self.analyze_database_scripts()
        print()
        
        self.analyze_environment_adaptation()
        print()
        
        self.analyze_adaptive_generation_capability()
        print()
        
        self.compare_scripts()
        print()
        
        self.generate_recommendations()
        print()
        
        # Generate summary
        self._generate_summary()
        
        # Save results
        self._save_results()
        
        print("Analysis complete!")
        return self.results
    
    def _generate_summary(self):
        """Generate executive summary"""
        comparison = self.results.get("script_comparison", {})
        env_adaptation = self.results.get("environment_adaptation", {})
        adaptive_gen = self.results.get("adaptive_generation_capability", {})
        
        # Answer the key questions
        all_scripts_in_db = (comparison.get("only_filesystem", 0) == 0 and 
                            comparison.get("content_matches", 0) == comparison.get("total_filesystem", 0))
        
        adaptive_capable = (adaptive_gen.get("script_templates", 0) > 0 or
                           adaptive_gen.get("parameter_substitution", False) or
                           env_adaptation.get("template_storage", False))
        
        summary = {
            "key_questions_answered": {
                "all_scripts_stored_in_db": all_scripts_in_db,
                "explanation_script_storage": self._explain_script_storage(),
                "can_generate_adaptive_scripts": adaptive_capable,
                "explanation_adaptive_capability": self._explain_adaptive_capability()
            },
            "metrics": {
                "filesystem_scripts": comparison.get("total_filesystem", 0),
                "database_scripts": comparison.get("total_database", 0), 
                "synchronized_scripts": comparison.get("content_matches", 0),
                "environment_aware_scripts": env_adaptation.get("environment_aware_scripts", 0),
                "template_scripts": adaptive_gen.get("script_templates", 0)
            },
            "recommendations_count": len(self.results.get("recommendations", []))
        }
        
        self.results["executive_summary"] = summary
    
    def _explain_script_storage(self):
        """Explain script storage status"""
        comparison = self.results.get("script_comparison", {})
        
        if comparison.get("only_filesystem", 0) == 0:
            return "ALL scripts are stored in production.db with current content"
        elif comparison.get("in_both", 0) > 0:
            return f"PARTIAL storage: {comparison.get('in_both', 0)} scripts in both locations, {comparison.get('only_filesystem', 0)} only in filesystem"
        else:
            return "MINIMAL storage: Most scripts only exist in filesystem"
    
    def _explain_adaptive_capability(self):
        """Explain adaptive script generation capability"""
        adaptive_gen = self.results.get("adaptive_generation_capability", {})
        env_adaptation = self.results.get("environment_adaptation", {})
        
        capabilities = []
        
        if adaptive_gen.get("parameter_substitution", False):
            capabilities.append("parameter substitution")
            
        if env_adaptation.get("template_storage", False):
            capabilities.append("template storage")
            
        if adaptive_gen.get("environment_variants", 0) > 0:
            capabilities.append("environment variants")
            
        if adaptive_gen.get("deployment_automation", False):
            capabilities.append("deployment automation")
        
        if capabilities:
            return f"YES - Supports: {', '.join(capabilities)}"
        else:
            return "LIMITED - Basic infrastructure present but not fully implemented"
    
    def _save_results(self):
        """Save analysis results to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save JSON report
        json_file = self.workspace_path / f"PRODUCTION_DB_SCRIPT_ANALYSIS_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        # Save markdown report  
        md_file = self.workspace_path / f"PRODUCTION_DB_SCRIPT_ANALYSIS_{timestamp}.md"
        with open(md_file, 'w', encoding='utf-8') as f:
            self._write_markdown_report(f)
        
        print(f"Results saved to:")
        print(f"  JSON: {json_file}")
        print(f"  Markdown: {md_file}")
    
    def _write_markdown_report(self, f):
        """Write markdown report"""
        summary = self.results.get("executive_summary", {})
        comparison = self.results.get("script_comparison", {})
        
        f.write("# Production Database Script Analysis Report\n\n")
        f.write(f"**Analysis Date:** {self.results['analysis_timestamp']}\n\n")
        
        f.write("## Executive Summary\n\n")
        
        # Key questions
        key_q = summary.get("key_questions_answered", {})
        f.write("### Key Questions Answered\n\n")
        f.write(f"**Q1: Are ALL code scripts stored in production.db?**\n")
        f.write(f"Answer: **{'YES' if key_q.get('all_scripts_stored_in_db') else 'NO'}**\n")
        f.write(f"Explanation: {key_q.get('explanation_script_storage', 'N/A')}\n\n")
        
        f.write(f"**Q2: Can the database generate environment-adaptive scripts?**\n")
        f.write(f"Answer: **{'YES' if key_q.get('can_generate_adaptive_scripts') else 'NO'}**\n") 
        f.write(f"Explanation: {key_q.get('explanation_adaptive_capability', 'N/A')}\n\n")
        
        # Metrics
        metrics = summary.get("metrics", {})
        f.write("### Key Metrics\n\n")
        f.write(f"- **Filesystem Scripts:** {metrics.get('filesystem_scripts', 0)}\n")
        f.write(f"- **Database Scripts:** {metrics.get('database_scripts', 0)}\n")
        f.write(f"- **Synchronized Scripts:** {metrics.get('synchronized_scripts', 0)}\n")
        f.write(f"- **Environment-Aware Scripts:** {metrics.get('environment_aware_scripts', 0)}\n")
        f.write(f"- **Template Scripts:** {metrics.get('template_scripts', 0)}\n\n")
        
        # Detailed comparison
        f.write("## Script Comparison Details\n\n")
        f.write(f"- **Total in Filesystem:** {comparison.get('total_filesystem', 0)}\n")
        f.write(f"- **Total in Database:** {comparison.get('total_database', 0)}\n")
        f.write(f"- **In Both Locations:** {comparison.get('in_both', 0)}\n")
        f.write(f"- **Only in Filesystem:** {comparison.get('only_filesystem', 0)}\n")
        f.write(f"- **Only in Database:** {comparison.get('only_database', 0)}\n")
        f.write(f"- **Content Matches:** {comparison.get('content_matches', 0)}\n")
        f.write(f"- **Content Differs:** {comparison.get('content_differs', 0)}\n\n")
        
        # Recommendations
        recommendations = self.results.get("recommendations", [])
        if recommendations:
            f.write("## Recommendations\n\n")
            for i, rec in enumerate(recommendations, 1):
                f.write(f"### {i}. {rec.get('type', 'Unknown')} ({rec.get('priority', 'UNKNOWN')} Priority)\n")
                f.write(f"**Issue:** {rec.get('issue', 'N/A')}\n\n")
                f.write(f"**Recommendation:** {rec.get('recommendation', 'N/A')}\n\n")

def main():
    workspace_path = r"e:\_copilot_sandbox"
    
    analyzer = ProductionDBScriptAnalyzer(workspace_path)
    results = analyzer.run_complete_analysis()
    
    # Print key findings
    print("\n" + "=" * 60)
    print("KEY FINDINGS SUMMARY")
    print("=" * 60)
    
    summary = results.get("executive_summary", {})
    key_q = summary.get("key_questions_answered", {})
    
    print(f"\nQ1: Are ALL code scripts stored in production.db?")
    print(f"Answer: {'YES' if key_q.get('all_scripts_stored_in_db') else 'NO'}")
    print(f"Details: {key_q.get('explanation_script_storage', 'N/A')}")
    
    print(f"\nQ2: Can the database generate environment-adaptive scripts?")
    print(f"Answer: {'YES' if key_q.get('can_generate_adaptive_scripts') else 'NO'}")
    print(f"Details: {key_q.get('explanation_adaptive_capability', 'N/A')}")
    
    metrics = summary.get("metrics", {})
    print(f"\nScript Metrics:")
    print(f"  - Filesystem: {metrics.get('filesystem_scripts', 0)}")
    print(f"  - Database: {metrics.get('database_scripts', 0)}")
    print(f"  - Synchronized: {metrics.get('synchronized_scripts', 0)}")
    
    recommendations = results.get("recommendations", [])
    print(f"\nRecommendations: {len(recommendations)} items identified")
    
    return results

if __name__ == "__main__":
    main()
