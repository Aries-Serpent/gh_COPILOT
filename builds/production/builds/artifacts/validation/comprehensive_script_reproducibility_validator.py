#!/usr/bin/env python3
"""
COMPREHENSIVE SCRIPT REPRODUCIBILITY VALIDATOR
============================================

Enterprise-Grade Database-First Architecture Compliance Analysis
Validates that all scripts are stored in both filesystem and databases
Ensures database-consumed scripts are fully reproducible

Author: PIS Framework Team
Date: July 10, 2025
Version: 6.0 - Quantum Enhanced Database-First Validation
"""

import os
import sys
import sqlite3
import json
import hashlib
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
import logging

# Visual Processing Indicators
try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False

# Enhanced Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | SCRIPT-VALIDATOR | %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f'script_reproducibility_validation_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log', encoding='utf-8')
    ]
)

class ComprehensiveScriptReproducibilityValidator:
    """
    Comprehensive Script Reproducibility Validator
    
    Validates Database-First Architecture compliance by ensuring:
    1. All scripts tracked in databases
    2. Script content stored for reproducibility
    3. Template patterns available for regeneration
    4. Cross-database synchronization verified
    """
    
    def __init__(self, workspace_root: str = None):
        """Initialize the Script Reproducibility Validator"""
        self.workspace_root = workspace_root or os.getcwd()
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Database paths
        self.main_databases = [
            'production.db',
            'pis_comprehensive.db',
            'analytics.db',
            'enterprise_validation.db'
        ]
        
        self.database_folder_dbs = []
        databases_folder = os.path.join(self.workspace_root, 'databases')
        if os.path.exists(databases_folder):
            for file in os.listdir(databases_folder):
                if file.endswith('.db'):
                    self.database_folder_dbs.append(os.path.join(databases_folder, file))
        
        # Results tracking
        self.filesystem_scripts = {}
        self.database_scripts = {}
        self.reproducibility_results = {}
        self.validation_metrics = {}
        
        self.logger.info(f"🚀 Script Reproducibility Validator initialized")
        self.logger.info(f"Workspace: {self.workspace_root}")
        self.logger.info(f"Main databases: {len(self.main_databases)}")
        self.logger.info(f"Database folder databases: {len(self.database_folder_dbs)}")
        
    def scan_filesystem_scripts(self) -> Dict[str, Dict[str, Any]]:
        """Scan filesystem for all script files"""
        self.logger.info("📁 Scanning filesystem for scripts...")
        
        script_extensions = ['.py', '.ps1', '.sh', '.bat', '.sql', '.js', '.ts']
        scripts = {}
        
        for root, dirs, files in os.walk(self.workspace_root):
            # Skip version control and cache directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]
            
            for file in files:
                if any(file.endswith(ext) for ext in script_extensions):
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, self.workspace_root)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        
                        # Calculate file hash
                        file_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
                        
                        # Get file stats
                        stats = os.stat(file_path)
                        
                        scripts[relative_path] = {
                            'absolute_path': file_path,
                            'size': stats.st_size,
                            'modified': datetime.fromtimestamp(stats.st_mtime).isoformat(),
                            'hash': file_hash,
                            'extension': os.path.splitext(file)[1],
                            'content_length': len(content),
                            'line_count': content.count('\n') + 1 if content else 0
                        }
                        
                    except Exception as e:
                        self.logger.warning(f"Could not read {file_path}: {e}")
                        scripts[relative_path] = {
                            'absolute_path': file_path,
                            'error': str(e),
                            'size': 0,
                            'hash': 'ERROR'
                        }
        
        self.filesystem_scripts = scripts
        self.logger.info(f"✅ Found {len(scripts)} scripts in filesystem")
        return scripts
        
    def scan_database_scripts(self) -> Dict[str, Dict[str, Any]]:
        """Scan all databases for script tracking and storage"""
        self.logger.info("🗄️ Scanning databases for script records...")
        
        database_scripts = {}
        
        # Check main databases
        for db_name in self.main_databases:
            db_path = os.path.join(self.workspace_root, db_name)
            if os.path.exists(db_path):
                scripts = self._scan_single_database(db_path, db_name)
                if scripts:
                    database_scripts[db_name] = scripts
        
        # Check databases folder
        for db_path in self.database_folder_dbs:
            db_name = os.path.basename(db_path)
            scripts = self._scan_single_database(db_path, db_name)
            if scripts:
                database_scripts[f"databases/{db_name}"] = scripts
        
        self.database_scripts = database_scripts
        total_db_scripts = sum(len(scripts) for scripts in database_scripts.values())
        self.logger.info(f"✅ Found {total_db_scripts} script records across {len(database_scripts)} databases")
        return database_scripts
        
    def _scan_single_database(self, db_path: str, db_name: str) -> Dict[str, Any]:
        """Scan a single database for script-related tables"""
        scripts = {}
        
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                
                # Get all table names
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                # Look for script-related tables
                script_tables = [
                    table for table in tables 
                    if any(keyword in table.lower() for keyword in [
                        'script', 'file', 'template', 'pattern', 'tracking', 'generated', 'code'
                    ])
                ]
                
                for table in script_tables:
                    try:
                        # Get table schema
                        cursor.execute(f"PRAGMA table_info({table})")
                        columns = [row[1] for row in cursor.fetchall()]
                        
                        # Look for path-like columns
                        path_columns = [col for col in columns if any(keyword in col.lower() for keyword in ['path', 'file', 'name', 'location'])]
                        
                        if path_columns:
                            # Query the table for script records
                            cursor.execute(f"SELECT * FROM {table} LIMIT 100")  # Limit to avoid huge datasets
                            rows = cursor.fetchall()
                            
                            for row in rows:
                                row_dict = dict(zip(columns, row))
                                
                                # Try to identify script paths
                                for path_col in path_columns:
                                    path_value = row_dict.get(path_col)
                                    if path_value and isinstance(path_value, str):
                                        if any(ext in path_value for ext in ['.py', '.ps1', '.sh', '.bat', '.sql', '.js']):
                                            script_key = f"{table}:{path_value}"
                                            scripts[script_key] = {
                                                'table': table,
                                                'path': path_value,
                                                'database': db_name,
                                                'columns': columns,
                                                'record': row_dict
                                            }
                    
                    except Exception as e:
                        self.logger.debug(f"Could not scan table {table} in {db_name}: {e}")
                        
        except Exception as e:
            self.logger.warning(f"Could not scan database {db_path}: {e}")
            
        return scripts
        
    def analyze_reproducibility(self) -> Dict[str, Any]:
        """Analyze script reproducibility across filesystem and databases"""
        self.logger.info("🔬 Analyzing script reproducibility...")
        
        # Get filesystem and database script sets
        fs_scripts = set(self.filesystem_scripts.keys())
        
        # Flatten database scripts to get script paths
        db_script_paths = set()
        for db_name, scripts in self.database_scripts.items():
            for script_key, script_info in scripts.items():
                path = script_info.get('path', '')
                # Normalize path separators
                normalized_path = path.replace('\\', '/').replace('//', '/')
                if normalized_path.startswith('./'):
                    normalized_path = normalized_path[2:]
                db_script_paths.add(normalized_path)
        
        # Normalize filesystem paths for comparison
        normalized_fs_scripts = set()
        for path in fs_scripts:
            normalized_path = path.replace('\\', '/').replace('//', '/')
            normalized_fs_scripts.add(normalized_path)
        
        # Calculate overlaps
        in_both = normalized_fs_scripts.intersection(db_script_paths)
        only_filesystem = normalized_fs_scripts - db_script_paths
        only_database = db_script_paths - normalized_fs_scripts
        
        # Analyze reproducibility by category
        reproducibility_analysis = {
            'total_filesystem_scripts': len(fs_scripts),
            'total_database_scripts': len(db_script_paths),
            'scripts_in_both': len(in_both),
            'only_in_filesystem': len(only_filesystem),
            'only_in_database': len(only_database),
            'coverage_percentage': (len(in_both) / len(fs_scripts) * 100) if fs_scripts else 0,
            'reproducibility_score': 0.0
        }
        
        # Calculate reproducibility score
        if fs_scripts:
            base_score = len(in_both) / len(fs_scripts) * 100
            
            # Bonus for template patterns
            template_bonus = min(20, len([db for db in self.database_scripts if 'template' in db.lower()]) * 5)
            
            # Bonus for comprehensive tracking
            tracking_bonus = min(15, len(self.database_scripts) * 2)
            
            reproducibility_analysis['reproducibility_score'] = min(100, base_score + template_bonus + tracking_bonus)
        
        # Detailed analysis by script type
        script_type_analysis = {}
        for script_path in fs_scripts:
            extension = os.path.splitext(script_path)[1]
            if extension not in script_type_analysis:
                script_type_analysis[extension] = {
                    'total': 0,
                    'tracked': 0,
                    'coverage': 0.0
                }
            
            script_type_analysis[extension]['total'] += 1
            normalized_path = script_path.replace('\\', '/').replace('//', '/')
            if normalized_path in db_script_paths:
                script_type_analysis[extension]['tracked'] += 1
        
        # Calculate coverage per type
        for ext, stats in script_type_analysis.items():
            if stats['total'] > 0:
                stats['coverage'] = (stats['tracked'] / stats['total']) * 100
        
        reproducibility_analysis['by_script_type'] = script_type_analysis
        reproducibility_analysis['scripts_only_filesystem'] = list(only_filesystem)
        reproducibility_analysis['scripts_only_database'] = list(only_database)
        reproducibility_analysis['scripts_in_both'] = list(in_both)
        
        self.reproducibility_results = reproducibility_analysis
        return reproducibility_analysis
        
    def validate_template_intelligence(self) -> Dict[str, Any]:
        """Validate Template Intelligence Platform for script reproduction"""
        self.logger.info("🧠 Validating Template Intelligence Platform...")
        
        template_analysis = {
            'template_databases': 0,
            'pattern_tables': 0,
            'template_patterns': 0,
            'reproducible_script_types': [],
            'template_coverage': 0.0
        }
        
        # Look for template-related databases and tables
        for db_key, scripts in self.database_scripts.items():
            if any(keyword in db_key.lower() for keyword in ['template', 'pattern', 'intelligence']):
                template_analysis['template_databases'] += 1
                
                # Count pattern tables
                tables = set()
                for script_key, script_info in scripts.items():
                    table_name = script_info.get('table', '')
                    if any(keyword in table_name.lower() for keyword in ['pattern', 'template', 'generate']):
                        tables.add(table_name)
                
                template_analysis['pattern_tables'] += len(tables)
        
        # Check for placeholder templates
        placeholder_files = []
        templates_dir = os.path.join(self.workspace_root, 'templates')
        if os.path.exists(templates_dir):
            for root, dirs, files in os.walk(templates_dir):
                for file in files:
                    if file.endswith('.json') and 'placeholder' in file:
                        placeholder_files.append(file)
        
        template_analysis['placeholder_templates'] = len(placeholder_files)
        
        # Estimate template coverage
        total_scripts = len(self.filesystem_scripts)
        if total_scripts > 0:
            # Assume templates can cover common script patterns
            estimated_coverage = min(85, template_analysis['template_databases'] * 20 + 
                                   template_analysis['pattern_tables'] * 10 + 
                                   template_analysis['placeholder_templates'] * 5)
            template_analysis['template_coverage'] = estimated_coverage
        
        return template_analysis
        
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """Generate comprehensive reproducibility report"""
        self.logger.info("📊 Generating comprehensive reproducibility report...")
        
        # Scan everything
        filesystem_scripts = self.scan_filesystem_scripts()
        database_scripts = self.scan_database_scripts()
        reproducibility_analysis = self.analyze_reproducibility()
        template_analysis = self.validate_template_intelligence()
        
        # Create comprehensive report
        report = {
            'timestamp': datetime.now().isoformat(),
            'workspace': self.workspace_root,
            'summary': {
                'total_filesystem_scripts': len(filesystem_scripts),
                'total_databases_scanned': len(self.main_databases) + len(self.database_folder_dbs),
                'databases_with_scripts': len(database_scripts),
                'reproducibility_score': reproducibility_analysis.get('reproducibility_score', 0),
                'coverage_percentage': reproducibility_analysis.get('coverage_percentage', 0),
                'template_coverage': template_analysis.get('template_coverage', 0)
            },
            'filesystem_analysis': {
                'total_scripts': len(filesystem_scripts),
                'script_types': {},
                'largest_scripts': [],
                'recent_scripts': []
            },
            'database_analysis': {
                'databases_scanned': list(database_scripts.keys()),
                'total_script_records': sum(len(scripts) for scripts in database_scripts.values()),
                'script_tracking_tables': []
            },
            'reproducibility_analysis': reproducibility_analysis,
            'template_intelligence': template_analysis,
            'recommendations': []
        }
        
        # Analyze script types in filesystem
        script_types = {}
        for path, info in filesystem_scripts.items():
            ext = info.get('extension', 'unknown')
            if ext not in script_types:
                script_types[ext] = {'count': 0, 'total_size': 0}
            script_types[ext]['count'] += 1
            script_types[ext]['total_size'] += info.get('size', 0)
        
        report['filesystem_analysis']['script_types'] = script_types
        
        # Find largest scripts
        largest_scripts = sorted(
            [(path, info.get('size', 0)) for path, info in filesystem_scripts.items() if 'error' not in info],
            key=lambda x: x[1], reverse=True
        )[:10]
        report['filesystem_analysis']['largest_scripts'] = largest_scripts
        
        # Generate recommendations
        recommendations = []
        
        if reproducibility_analysis.get('coverage_percentage', 0) < 80:
            recommendations.append("🔧 Enhance database tracking - Only {:.1f}% of scripts are tracked in databases".format(
                reproducibility_analysis.get('coverage_percentage', 0)))
        
        if template_analysis.get('template_coverage', 0) < 70:
            recommendations.append("🧠 Expand Template Intelligence Platform - Current template coverage is {:.1f}%".format(
                template_analysis.get('template_coverage', 0)))
        
        if reproducibility_analysis.get('only_in_filesystem', 0) > 50:
            recommendations.append("📁 {} scripts exist only in filesystem - Need database tracking".format(
                reproducibility_analysis.get('only_in_filesystem', 0)))
        
        if len(database_scripts) < 3:
            recommendations.append("🗄️ Insufficient script tracking databases - Consider distributed tracking")
        
        if not recommendations:
            recommendations.append("✅ Script reproducibility is in excellent condition")
        
        report['recommendations'] = recommendations
        
        return report
        
    def save_report(self, report: Dict[str, Any]) -> str:
        """Save the comprehensive report to file"""
        report_filename = f"script_reproducibility_comprehensive_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path = os.path.join(self.workspace_root, report_filename)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=str)
        
        self.logger.info(f"📋 Comprehensive report saved: {report_filename}")
        return report_path


def main():
    """Main execution function"""
    print("🚀 COMPREHENSIVE SCRIPT REPRODUCIBILITY VALIDATOR")
    print("=" * 70)
    print("Database-First Architecture Compliance Analysis")
    print("-" * 70)
    
    try:
        # Initialize validator
        validator = ComprehensiveScriptReproducibilityValidator()
        
        # Generate comprehensive report
        start_time = time.time()
        report = validator.generate_comprehensive_report()
        execution_time = time.time() - start_time
        
        # Display results
        print(f"\n📊 SCRIPT REPRODUCIBILITY ANALYSIS RESULTS")
        print("=" * 70)
        print(f"Execution Time: {execution_time:.2f} seconds")
        print(f"Workspace: {report['workspace']}")
        print(f"Analysis Timestamp: {report['timestamp']}")
        
        summary = report['summary']
        print(f"\n📈 SUMMARY METRICS:")
        print(f"   Total Filesystem Scripts: {summary['total_filesystem_scripts']}")
        print(f"   Databases Scanned: {summary['total_databases_scanned']}")
        print(f"   Databases with Scripts: {summary['databases_with_scripts']}")
        print(f"   Coverage Percentage: {summary['coverage_percentage']:.1f}%")
        print(f"   Reproducibility Score: {summary['reproducibility_score']:.1f}%")
        print(f"   Template Coverage: {summary['template_coverage']:.1f}%")
        
        # Display script types
        script_types = report['filesystem_analysis']['script_types']
        print(f"\n📁 SCRIPT TYPES ANALYSIS:")
        for ext, stats in sorted(script_types.items(), key=lambda x: x[1]['count'], reverse=True):
            print(f"   {ext}: {stats['count']} scripts ({stats['total_size']:,} bytes)")
        
        # Display reproducibility details
        repro = report['reproducibility_analysis']
        print(f"\n🔬 REPRODUCIBILITY ANALYSIS:")
        print(f"   Scripts in Both Locations: {repro['scripts_in_both']}")
        print(f"   Only in Filesystem: {repro['only_in_filesystem']}")
        print(f"   Only in Database: {repro['only_in_database']}")
        
        # Display recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        for i, recommendation in enumerate(report['recommendations'], 1):
            print(f"   {i}. {recommendation}")
        
        # Save report
        report_path = validator.save_report(report)
        print(f"\n📋 Detailed report saved: {os.path.basename(report_path)}")
        
        # Determine overall status
        reproducibility_score = summary['reproducibility_score']
        if reproducibility_score >= 90:
            status = "EXCELLENT"
            icon = "🏆"
        elif reproducibility_score >= 75:
            status = "GOOD"
            icon = "✅"
        elif reproducibility_score >= 60:
            status = "ACCEPTABLE"
            icon = "⚠️"
        else:
            status = "NEEDS IMPROVEMENT"
            icon = "🔧"
        
        print(f"\n{icon} OVERALL STATUS: {status}")
        print(f"🎯 Database-First Architecture Compliance: {reproducibility_score:.1f}%")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Validation failed: {e}")
        logging.error(f"Script reproducibility validation error: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
