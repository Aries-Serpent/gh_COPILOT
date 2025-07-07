#!/usr/bin/env python3
"""
Comprehensive Database Structure Analyzer
========================================

DUAL COPILOT PATTERN - Enterprise Database Analysis & Documentation
Part 1 of 3: Complete structural analysis of Enterprise 6-Step Framework databases

Features:
- SQLite3 database connectivity validation with integrity checks
- Complete table inventory with row counts and structural analysis
- Foreign key relationship identification and mapping
- Sample data extraction and analysis
- Comprehensive schema documentation generation
- Enterprise-grade error handling and visual progress indicators
- Markdown report generation with detailed findings

Enterprise Framework Integration:
- Analytics Collector DB (Step 3) - Analytics data aggregation
- Continuous Innovation DB (Step 6) - Innovation algorithms and results
- Learning Monitor DB (Step 2) - Learning patterns and behavior tracking  
- Performance Analysis DB (Step 4) - Performance metrics and optimization
- Capability Scaler DB (Step 5) - Capability scaling and resource management

Author: Enterprise Database Analysis System
Version: 1.0.0
"""

import os
import sys
import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
import logging
from tqdm import tqdm
import traceback

class ComprehensiveDatabaseAnalyzer:
    """Enterprise-grade database structure analysis and documentation system"""
    
    def __init__(self, databases_dir: Optional[str] = None):
        self.databases_dir = Path(databases_dir or os.path.join(os.getcwd(), "databases"))
        self.analysis_timestamp = datetime.now()
        self.session_id = f"DB_ANALYSIS_{int(self.analysis_timestamp.timestamp())}"
        
        # Results storage
        self.analysis_results = {
            "session_id": self.session_id,
            "timestamp": self.analysis_timestamp.isoformat(),
            "databases_directory": str(self.databases_dir),
            "total_databases": 0,
            "successful_analyses": 0,
            "failed_analyses": 0,
            "database_details": {},
            "summary_statistics": {},
            "errors": []
        }
        
        # Setup logging
        self.log_path = Path(os.getcwd()) / f"database_analysis_{self.session_id}.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(str(self.log_path)),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Expected Enterprise Framework databases
        self.expected_databases = {
            "analytics_collector.db": {
                "step": 3,
                "purpose": "Analytics collection and aggregation",
                "expected_tables": ["analytics_sources", "collected_data", "collection_sessions"]
            },
            "continuous_innovation.db": {
                "step": 6,
                "purpose": "Innovation algorithms and optimization results",
                "expected_tables": ["innovations", "implementations", "optimization_results"]
            },
            "learning_monitor.db": {
                "step": 2,
                "purpose": "Learning patterns and system behavior tracking",
                "expected_tables": ["learning_sessions", "behavioral_patterns", "system_adaptations"]
            },
            "performance_analysis.db": {
                "step": 4,
                "purpose": "Performance metrics and optimization recommendations",
                "expected_tables": ["analysis_sessions", "performance_metrics", "optimization_recommendations"]
            },
            "capability_scaler.db": {
                "step": 5,
                "purpose": "Capability scaling and resource management",
                "expected_tables": ["capabilities", "scaling_operations", "resource_utilization"]
            }
        }
        
        self.logger.info(f"[LAUNCH] Database Structure Analyzer initialized - Session: {self.session_id}")
        self.logger.info(f"[FOLDER] Target directory: {self.databases_dir}")
    
    def validate_database_integrity(self, db_path: Path) -> Tuple[bool, str]:
        """Validate database integrity using SQLite PRAGMA checks"""
        try:
            with sqlite3.connect(str(db_path)) as conn:
                cursor = conn.cursor()
                
                # Check database integrity
                cursor.execute("PRAGMA integrity_check")
                integrity_result = cursor.fetchone()
                
                if integrity_result and integrity_result[0].lower() == "ok":
                    return True, "Database integrity check passed"
                else:
                    return False, f"Database integrity check failed: {integrity_result[0] if integrity_result else 'Unknown error'}"
                    
        except sqlite3.Error as e:
            return False, f"SQLite error during integrity check: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error during integrity check: {str(e)}"
    
    def get_database_info(self, db_path: Path) -> Dict[str, Any]:
        """Extract comprehensive database information"""
        db_info = {
            "name": db_path.name,
            "path": str(db_path),
            "size_bytes": 0,
            "accessible": False,
            "integrity_status": "unknown",
            "tables": {},
            "total_records": 0,
            "foreign_keys": [],
            "schema_complexity": "unknown",
            "framework_step": None,
            "framework_purpose": None,
            "sample_data": {},
            "errors": []
        }
        
        try:
            # Basic file information
            if db_path.exists():
                db_info["size_bytes"] = db_path.stat().st_size
                db_info["modified_time"] = datetime.fromtimestamp(db_path.stat().st_mtime).isoformat()
            else:
                db_info["errors"].append("Database file does not exist")
                return db_info
            
            # Framework information
            if db_path.name in self.expected_databases:
                expected_info = self.expected_databases[db_path.name]
                db_info["framework_step"] = expected_info["step"]
                db_info["framework_purpose"] = expected_info["purpose"]
                db_info["expected_tables"] = expected_info["expected_tables"]
            
            # Integrity validation
            integrity_valid, integrity_message = self.validate_database_integrity(db_path)
            db_info["accessible"] = integrity_valid
            db_info["integrity_status"] = integrity_message
            
            if not integrity_valid:
                db_info["errors"].append(f"Integrity validation failed: {integrity_message}")
                return db_info
            
            # Connect to database for detailed analysis
            with sqlite3.connect(str(db_path)) as conn:
                cursor = conn.cursor()
                
                # Get all tables
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
                table_names = [row[0] for row in cursor.fetchall()]
                
                # Analyze each table
                total_records = 0
                for table_name in table_names:
                    table_info = self.analyze_table(cursor, table_name)
                    db_info["tables"][table_name] = table_info
                    total_records += table_info["row_count"]
                    
                    # Get sample data
                    sample_data = self.get_sample_data(cursor, table_name)
                    db_info["sample_data"][table_name] = sample_data
                
                db_info["total_records"] = total_records
                
                # Get foreign key information
                db_info["foreign_keys"] = self.get_foreign_keys(cursor, table_names)
                
                # Determine schema complexity
                db_info["schema_complexity"] = self.assess_schema_complexity(db_info)
                
        except sqlite3.Error as e:
            error_msg = f"SQLite error: {str(e)}"
            db_info["errors"].append(error_msg)
            self.logger.error(f"SQLite error analyzing {db_path.name}: {error_msg}")
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            db_info["errors"].append(error_msg)
            self.logger.error(f"Unexpected error analyzing {db_path.name}: {error_msg}")
        
        return db_info
    
    def analyze_table(self, cursor: sqlite3.Cursor, table_name: str) -> Dict[str, Any]:
        """Analyze individual table structure and content"""
        table_info = {
            "name": table_name,
            "row_count": 0,
            "columns": [],
            "primary_keys": [],
            "indexes": [],
            "creation_sql": ""
        }
        
        try:
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM [{table_name}]")
            table_info["row_count"] = cursor.fetchone()[0]
            
            # Get table schema
            cursor.execute(f"PRAGMA table_info([{table_name}])")
            columns = cursor.fetchall()
            
            for col in columns:
                column_info = {
                    "name": col[1],
                    "type": col[2],
                    "not_null": bool(col[3]),
                    "default_value": col[4],
                    "primary_key": bool(col[5])
                }
                table_info["columns"].append(column_info)
                
                if column_info["primary_key"]:
                    table_info["primary_keys"].append(column_info["name"])
            
            # Get indexes
            cursor.execute(f"PRAGMA index_list([{table_name}])")
            indexes = cursor.fetchall()
            for idx in indexes:
                table_info["indexes"].append({
                    "name": idx[1],
                    "unique": bool(idx[2])
                })
            
            # Get table creation SQL
            cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
            creation_sql = cursor.fetchone()
            if creation_sql:
                table_info["creation_sql"] = creation_sql[0]
            
        except sqlite3.Error as e:
            table_info["error"] = f"Error analyzing table {table_name}: {str(e)}"
        
        return table_info
    
    def get_sample_data(self, cursor: sqlite3.Cursor, table_name: str, limit: int = 5) -> List[Dict]:
        """Extract sample data from table"""
        try:
            cursor.execute(f"SELECT * FROM [{table_name}] LIMIT {limit}")
            rows = cursor.fetchall()
            
            # Get column names
            cursor.execute(f"PRAGMA table_info([{table_name}])")
            columns = [col[1] for col in cursor.fetchall()]
            
            # Convert rows to dictionaries
            sample_data = []
            for row in rows:
                row_dict = dict(zip(columns, row))
                sample_data.append(row_dict)
            
            return sample_data
            
        except sqlite3.Error as e:
            return [{"error": f"Error retrieving sample data: {str(e)}"}]
    
    def get_foreign_keys(self, cursor: sqlite3.Cursor, table_names: List[str]) -> List[Dict]:
        """Identify foreign key relationships"""
        foreign_keys = []
        
        for table_name in table_names:
            try:
                cursor.execute(f"PRAGMA foreign_key_list([{table_name}])")
                fk_info = cursor.fetchall()
                
                for fk in fk_info:
                    foreign_keys.append({
                        "table": table_name,
                        "column": fk[3],
                        "references_table": fk[2],
                        "references_column": fk[4],
                        "on_update": fk[5],
                        "on_delete": fk[6]
                    })
            except sqlite3.Error:
                continue
        
        return foreign_keys
    
    def assess_schema_complexity(self, db_info: Dict[str, Any]) -> str:
        """Assess database schema complexity"""
        table_count = len(db_info["tables"])
        total_columns = sum(len(table["columns"]) for table in db_info["tables"].values())
        foreign_key_count = len(db_info["foreign_keys"])
        
        if table_count <= 3 and total_columns <= 15 and foreign_key_count == 0:
            return "simple"
        elif table_count <= 8 and total_columns <= 50 and foreign_key_count <= 5:
            return "moderate"
        else:
            return "complex"
    
    def scan_databases(self) -> List[Path]:
        """Scan databases directory for all .db files"""
        self.logger.info(f"[SEARCH] Scanning for database files in: {self.databases_dir}")
        
        if not self.databases_dir.exists():
            self.logger.error(f"[ERROR] Databases directory does not exist: {self.databases_dir}")
            return []
        
        db_files = list(self.databases_dir.glob("*.db"))
        self.logger.info(f"[BAR_CHART] Found {len(db_files)} database files")
        
        return db_files
    
    def analyze_all_databases(self) -> Dict[str, Any]:
        """Perform comprehensive analysis of all databases"""
        self.logger.info("[LAUNCH] STARTING COMPREHENSIVE DATABASE STRUCTURE ANALYSIS")
        self.logger.info(f"[FOLDER] Analysis Session: {self.session_id}")
        self.logger.info(f"[TIME] Timestamp: {self.analysis_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Scan for database files
        db_files = self.scan_databases()
        self.analysis_results["total_databases"] = len(db_files)
        
        if not db_files:
            self.logger.warning("[WARNING] No database files found to analyze")
            return self.analysis_results
        
        # Analyze each database with progress bar
        self.logger.info("[BAR_CHART] Beginning database structure analysis...")
        
        with tqdm(total=len(db_files), desc="Analyzing Databases", unit="db") as pbar:
            for db_file in db_files:
                pbar.set_description(f"Analyzing {db_file.name}")
                
                try:
                    self.logger.info(f"[SEARCH] Analyzing database: {db_file.name}")
                    
                    # Perform comprehensive analysis
                    db_info = self.get_database_info(db_file)
                    self.analysis_results["database_details"][db_file.name] = db_info
                    
                    # Update counters
                    if db_info["accessible"] and not db_info["errors"]:
                        self.analysis_results["successful_analyses"] += 1
                        status = "[SUCCESS] SUCCESS"
                    else:
                        self.analysis_results["failed_analyses"] += 1
                        status = "[ERROR] FAILED"
                    
                    # Log results
                    self.logger.info(f"{status} | {db_info['name']} | Tables: {len(db_info['tables'])} | Records: {db_info['total_records']} | Complexity: {db_info['schema_complexity']}")
                    
                except Exception as e:
                    error_msg = f"Critical error analyzing {db_file.name}: {str(e)}"
                    self.logger.error(error_msg)
                    self.analysis_results["errors"].append(error_msg)
                    self.analysis_results["failed_analyses"] += 1
                
                pbar.update(1)
        
        # Generate summary statistics
        self.generate_summary_statistics()
        
        self.logger.info("[SUCCESS] COMPREHENSIVE DATABASE ANALYSIS COMPLETED")
        self.logger.info(f"[BAR_CHART] Total Databases: {self.analysis_results['total_databases']}")
        self.logger.info(f"[SUCCESS] Successful: {self.analysis_results['successful_analyses']}")
        self.logger.info(f"[ERROR] Failed: {self.analysis_results['failed_analyses']}")
        
        return self.analysis_results
    
    def generate_summary_statistics(self):
        """Generate comprehensive summary statistics"""
        stats = {
            "total_tables": 0,
            "total_records": 0,
            "total_columns": 0,
            "total_foreign_keys": 0,
            "complexity_distribution": {"simple": 0, "moderate": 0, "complex": 0},
            "framework_coverage": {},
            "database_sizes": {},
            "accessibility_status": {"accessible": 0, "inaccessible": 0}
        }
        
        for db_name, db_info in self.analysis_results["database_details"].items():
            # Basic statistics
            stats["total_tables"] += len(db_info["tables"])
            stats["total_records"] += db_info["total_records"]
            stats["total_foreign_keys"] += len(db_info["foreign_keys"])
            stats["database_sizes"][db_name] = db_info["size_bytes"]
            
            # Column count
            for table_info in db_info["tables"].values():
                stats["total_columns"] += len(table_info["columns"])
            
            # Complexity distribution
            if db_info["schema_complexity"] in stats["complexity_distribution"]:
                stats["complexity_distribution"][db_info["schema_complexity"]] += 1
            
            # Framework coverage
            if db_info["framework_step"]:
                stats["framework_coverage"][f"Step {db_info['framework_step']}"] = db_name
            
            # Accessibility
            if db_info["accessible"]:
                stats["accessibility_status"]["accessible"] += 1
            else:
                stats["accessibility_status"]["inaccessible"] += 1
        
        self.analysis_results["summary_statistics"] = stats
    
    def generate_markdown_report(self) -> str:
        """Generate comprehensive markdown report"""
        report_path = Path(os.getcwd()) / f"database_structure_analysis_report_{self.session_id}.md"
        
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(self.build_markdown_content())
            
            self.logger.info(f"[?] Comprehensive report generated: {report_path}")
            return str(report_path)
            
        except Exception as e:
            self.logger.error(f"Error generating markdown report: {str(e)}")
            return ""
    
    def build_markdown_content(self) -> str:
        """Build comprehensive markdown report content"""
        content = f"""# Comprehensive Database Structure Analysis Report
===============================================

## Executive Summary

**Analysis Session:** {self.session_id}  
**Timestamp:** {self.analysis_timestamp.strftime('%Y-%m-%d %H:%M:%S')}  
**Target Directory:** `{self.databases_dir}`  
**Total Databases:** {self.analysis_results['total_databases']}  
**Successful Analyses:** {self.analysis_results['successful_analyses']}  
**Failed Analyses:** {self.analysis_results['failed_analyses']}  

## Summary Statistics

"""
        
        stats = self.analysis_results["summary_statistics"]
        content += f"""
| Metric | Value |
|--------|-------|
| Total Tables | {stats['total_tables']} |
| Total Records | {stats['total_records']:,} |
| Total Columns | {stats['total_columns']} |
| Total Foreign Keys | {stats['total_foreign_keys']} |
| Accessible Databases | {stats['accessibility_status']['accessible']} |
| Inaccessible Databases | {stats['accessibility_status']['inaccessible']} |

### Schema Complexity Distribution
- **Simple:** {stats['complexity_distribution']['simple']} databases
- **Moderate:** {stats['complexity_distribution']['moderate']} databases
- **Complex:** {stats['complexity_distribution']['complex']} databases

### Enterprise Framework Coverage
"""
        
        for step, db_name in stats["framework_coverage"].items():
            content += f"- **{step}:** {db_name}\n"
        
        content += "\n## Detailed Database Analysis\n\n"
        
        # Detailed analysis for each database
        for db_name, db_info in self.analysis_results["database_details"].items():
            content += f"""
### Database: `{db_name}`

**Status:** {'[SUCCESS] Accessible' if db_info['accessible'] else '[ERROR] Inaccessible'}  
**Size:** {db_info['size_bytes']:,} bytes  
**Tables:** {len(db_info['tables'])}  
**Total Records:** {db_info['total_records']:,}  
**Schema Complexity:** {db_info['schema_complexity'].title()}  
**Framework Step:** {f"Step {db_info['framework_step']}" if db_info['framework_step'] else "Unknown"}  
**Purpose:** {db_info['framework_purpose'] or "Not specified"}  

"""
            
            if db_info['errors']:
                content += "**Errors:**\n"
                for error in db_info['errors']:
                    content += f"- {error}\n"
                content += "\n"
            
            if db_info['tables']:
                content += "#### Tables:\n\n"
                for table_name, table_info in db_info['tables'].items():
                    content += f"""
**Table: `{table_name}`**
- Rows: {table_info['row_count']:,}
- Columns: {len(table_info['columns'])}
- Primary Keys: {', '.join(table_info['primary_keys']) if table_info['primary_keys'] else 'None'}

**Columns:**
"""
                    for col in table_info['columns']:
                        pk_indicator = " (PK)" if col['primary_key'] else ""
                        null_indicator = " NOT NULL" if col['not_null'] else ""
                        content += f"- `{col['name']}` {col['type']}{pk_indicator}{null_indicator}\n"
                    
                    # Sample data
                    if db_name in self.analysis_results["database_details"] and table_name in db_info['sample_data']:
                        sample_data = db_info['sample_data'][table_name]
                        if sample_data and not any('error' in str(row) for row in sample_data):
                            content += "\n**Sample Data (First 5 rows):**\n\n"
                            if sample_data:
                                # Create table header
                                headers = list(sample_data[0].keys())
                                content += "| " + " | ".join(headers) + " |\n"
                                content += "| " + " | ".join(["---"] * len(headers)) + " |\n"
                                
                                # Add data rows
                                for row in sample_data[:5]:
                                    values = [str(row.get(header, "")) for header in headers]
                                    content += "| " + " | ".join(values) + " |\n"
                            content += "\n"
                    
                    content += "\n"
            
            if db_info['foreign_keys']:
                content += "#### Foreign Key Relationships:\n\n"
                for fk in db_info['foreign_keys']:
                    content += f"- `{fk['table']}.{fk['column']}` [?] `{fk['references_table']}.{fk['references_column']}`\n"
                content += "\n"
        
        content += f"""
## Analysis Metadata

**Log File:** `{self.log_path}`  
**Analysis Tool:** Comprehensive Database Structure Analyzer v1.0.0  
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  

---
*Enterprise 6-Step Framework Database Analysis*  
*Part 1 of 3: Database Structure Analysis Complete*
"""
        
        return content
    
    def run_complete_analysis(self) -> bool:
        """Execute complete database structure analysis"""
        try:
            # Perform analysis
            results = self.analyze_all_databases()
            
            # Generate markdown report
            report_path = self.generate_markdown_report()
            
            # Print console summary
            self.print_console_summary()
            
            # Save JSON results
            json_path = Path(os.getcwd()) / f"database_analysis_results_{self.session_id}.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"[BAR_CHART] Analysis results saved: {json_path}")
            
            if report_path:
                self.logger.info(f"[?] Markdown report: {report_path}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Critical error during analysis: {str(e)}")
            self.logger.error(traceback.format_exc())
            return False
    
    def print_console_summary(self):
        """Print formatted console summary"""
        print("\n" + "="*80)
        print("[TARGET] COMPREHENSIVE DATABASE STRUCTURE ANALYSIS - SUMMARY")
        print("="*80)
        
        for db_name, db_info in self.analysis_results["database_details"].items():
            status = "accessible" if db_info["accessible"] else "corrupted" if db_info["errors"] else "empty"
            print(f"DATABASE: {db_name}")
            print(f"STATUS: {status}")
            print(f"TABLES: {len(db_info['tables'])}")
            print(f"TOTAL_RECORDS: {db_info['total_records']:,}")
            print(f"SCHEMA_COMPLEXITY: {db_info['schema_complexity']}")
            print("-" * 40)
        
        stats = self.analysis_results["summary_statistics"]
        print(f"\n[BAR_CHART] OVERALL STATISTICS:")
        print(f"Total Databases Analyzed: {self.analysis_results['total_databases']}")
        print(f"Total Tables: {stats['total_tables']}")
        print(f"Total Records: {stats['total_records']:,}")
        print(f"Total Columns: {stats['total_columns']}")
        print(f"Successful Analyses: {self.analysis_results['successful_analyses']}")
        print(f"Failed Analyses: {self.analysis_results['failed_analyses']}")
        print("="*80)

def main():
    """Main execution function"""
    print("Comprehensive Database Structure Analyzer")
    print("========================================")
    print("Enterprise 6-Step Framework - Database Analysis Tool")
    print("Part 1 of 3: Database Structure Analysis\n")
    
    # Initialize analyzer
    analyzer = ComprehensiveDatabaseAnalyzer()
    
    # Run complete analysis
    success = analyzer.run_complete_analysis()
    
    if success:
        print("\n[SUCCESS] Database structure analysis completed successfully!")
        print("[?] Comprehensive report and JSON results generated.")
        print("[TARGET] Ready for Part 2 of 3: Database Query Validation & Performance Testing")
    else:
        print("\n[ERROR] Database structure analysis completed with errors.")
        print("[CLIPBOARD] Please review log files for detailed error information.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
