#!/usr/bin/env python3
"""
ENTERPRISE PHASE DATABASE EXECUTOR
==================================
Database-First Phase 3-5 Execution with Comprehensive Terminal Logging
and Script Storage Integration

DUAL COPILOT PATTERN: Primary executor with database validation
DATABASE-FIRST ARCHITECTURE: All scripts stored and retrieved from production.db
TERMINAL LOGGING: Complete capture and analysis of execution output

Author: Enterprise GitHub Copilot Framework
Version: 1.0.0-DATABASE-FIRST
"""


import sys
import json
import sqlite3
import subprocess
import logging



from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
import hashlib


# Enterprise Configuration
ENTERPRISE_CONFIG = {
    "execution_timeout": 1800,  # 30 minutes per phase
    "log_level": "INFO",
    "database_path": "databases/production.db",
    "analytics_db": "databases/analytics.db",
    "backup_retention_days": 30,
    "visual_indicators": True,
    "anti_recursion": True,
    "database_first": True
}


@dataclass
class PhaseExecutionResult:
    """Enterprise phase execution result with database integration"""
    phase_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    success: bool = False
    return_code: int = -1
    stdout_log_path: str = ""
    stderr_log_path: str = ""
    database_script_stored: bool = False
    database_script_hash: str = ""
    metrics: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)


class EnterprisePhaseDatabaseExecutor:
    """
    DATABASE-FIRST PHASE EXECUTOR

    Executes Phases 3, 4, 5 with:
    - Complete terminal output logging
    - Database script storage and validation
    - Real-time progress monitoring
    - Enterprise compliance tracking
    """

    def __init__(self):
        self.workspace_root = Path.cwd()
        self.execution_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.logs_dir = self.workspace_root / 'logs' / 'phase_execution'
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        # Database paths
        self.production_db = self.workspace_root / ENTERPRISE_CONFIG["database_path"]
        self.analytics_db = self.workspace_root / ENTERPRISE_CONFIG["analytics_db"]

        # Phase configuration
        self.phases = {
            "phase3": {
                "script": "phase3_systematic_style_compliance.py",
                "name": "Systematic Style Compliance",
                "timeout": 900
            },
            "phase4": {
                "script": "phase4_enterprise_validation.py",
                "name": "Enterprise Validation & Reporting",
                "timeout": 1200
            },
            "phase5": {
                "script": "phase5_continuous_operation.py",
                "name": "Continuous Operation Mode",
                "timeout": 600
            }
        }

        self._setup_logging()
        self._initialize_databases()

    def _setup_logging(self):
        """Setup comprehensive logging with visual indicators"""
        log_file = self.logs_dir / f"enterprise_phase_execution_{self.execution_id}.log"

        logging.basicConfig(
            level=getattr(logging, ENTERPRISE_CONFIG["log_level"]),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )

        self.logger = logging.getLogger("EnterprisePhaseDatabaseExecutor")
        self.logger.info(f"[INIT] Enterprise Phase Database Executor - ID: {self.execution_id}")

    def _initialize_databases(self):
        """Initialize database connections and verify schema"""
        try:
            # Ensure databases exist
            self.production_db.parent.mkdir(parents=True, exist_ok=True)
            self.analytics_db.parent.mkdir(parents=True, exist_ok=True)

            # Verify production.db schema
            with sqlite3.connect(self.production_db) as conn:
                cursor = conn.cursor()

                # Check for required tables
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]

                required_tables = [
                    'file_system_mapping', 'script_templates', 'script_metadata',
                    'generated_scripts', 'codebase_analysis'
                ]

                missing_tables = [t for t in required_tables if t not in tables]
                if missing_tables:
                    self.logger.warning(f"[WARNING] Missing database tables: {missing_tables}")
                    self._create_missing_tables(cursor, missing_tables)
                    conn.commit()

                # Create phase execution tracking table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS phase_executions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        execution_id TEXT NOT NULL,
                        phase_id TEXT NOT NULL,
                        script_path TEXT NOT NULL,
                        start_time TIMESTAMP NOT NULL,
                        end_time TIMESTAMP,
                        status TEXT NOT NULL,
                        return_code INTEGER,
                        stdout_log_path TEXT,
                        stderr_log_path TEXT,
                        script_hash TEXT,
                        metrics TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                conn.commit()

            self.logger.info("[SUCCESS] Database initialization completed")

        except Exception as e:
            self.logger.error(f"[ERROR] Database initialization failed: {e}")
            raise

    def _create_missing_tables(self, cursor, missing_tables):
        """Create missing database tables for script storage"""
        table_schemas = {
            'file_system_mapping': '''
                CREATE TABLE file_system_mapping (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT UNIQUE NOT NULL,
                    file_content TEXT,
                    file_hash TEXT,
                    file_size INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'active',
                    file_type TEXT,
                    backup_location TEXT,
                    compression_type TEXT,
                    encoding TEXT DEFAULT 'utf-8'
                )
            ''',
            'script_templates': '''
                CREATE TABLE script_templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    template_name TEXT UNIQUE NOT NULL,
                    template_type TEXT NOT NULL DEFAULT 'script',
                    category TEXT NOT NULL,
                    description TEXT,
                    base_template TEXT NOT NULL,
                    variables TEXT DEFAULT '[]',
                    dependencies TEXT DEFAULT '[]',
                    compliance_patterns TEXT DEFAULT '[]',
                    complexity_level INTEGER DEFAULT 1,
                    author TEXT DEFAULT 'Enterprise Framework',
                    version TEXT DEFAULT '1.0.0',
                    tags TEXT DEFAULT '[]',
                    created_timestamp TEXT NOT NULL,
                    updated_timestamp TEXT NOT NULL,
                    active BOOLEAN DEFAULT 1
                )
            ''',
            'script_metadata': '''
                CREATE TABLE script_metadata (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filepath TEXT UNIQUE,
                    filename TEXT,
                    size_bytes INTEGER,
                    lines_of_code INTEGER,
                    functions TEXT,
                    classes TEXT,
                    imports TEXT,
                    dependencies TEXT,
                    patterns TEXT,
                    database_connections TEXT,
                    complexity_score INTEGER,
                    last_modified TEXT,
                    category TEXT,
                    analysis_timestamp TEXT
                )
            '''
        }

        for table in missing_tables:
            if table in table_schemas:
                cursor.execute(table_schemas[table])
                self.logger.info(f"[SUCCESS] Created missing table: {table}")

    def store_script_in_database(self, script_path: Path) -> Tuple[bool, str]:
        """Store script content in database with hash validation"""
        try:
            if not script_path.exists():
                return False, f"Script not found: {script_path}"

            # Read script content
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Calculate hash
            content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()

            # Store in database
            with sqlite3.connect(self.production_db) as conn:
                cursor = conn.cursor()

                # Insert or update file_system_mapping
                cursor.execute('''
                    INSERT OR REPLACE INTO file_system_mapping
                    (
                     file_path,
                     file_content,
                     file_hash,
                     file_size,
                     updated_at,
                     status,
                     file_type
                    (file_path, file_con)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    str(script_path),
                    content,
                    content_hash,
                    len(content.encode('utf-8')),
                    datetime.now().isoformat(),
                    'active',
                    'python_script'
                ))

                conn.commit()

            self.logger.info(f"[SUCCESS] Script stored in database: {script_path.name}")
            return True, content_hash

        except Exception as e:
            error_msg = f"Failed to store script in database: {e}"
            self.logger.error(f"[ERROR] {error_msg}")
            return False, error_msg

    def execute_phase_with_logging(self, phase_id: str) -> PhaseExecutionResult:
        """Execute phase with comprehensive terminal logging"""
        phase_config = self.phases[phase_id]
        script_path = self.workspace_root / phase_config["script"]

        result = PhaseExecutionResult(
            phase_id=phase_id,
            start_time=datetime.now()
        )

        # Setup log file paths
        log_timestamp = result.start_time.strftime('%Y%m%d_%H%M%S')
        result.stdout_log_path = str(self.logs_dir / f"{phase_id}_stdout_{log_timestamp}.log")
        result.stderr_log_path = str(self.logs_dir / f"{phase_id}_stderr_{log_timestamp}.log")

        self.logger.info(f"[START] Executing {phase_config['name']} ({phase_id})")
        self.logger.info(f"Script: {script_path}")
        self.logger.info(f"Timeout: {phase_config['timeout']} seconds")

        # Store script in database before execution
        stored, script_hash = self.store_script_in_database(script_path)
        result.database_script_stored = stored
        result.database_script_hash = script_hash

        try:
            # Execute phase with output capture
            with open(result.stdout_log_path, 'w', encoding='utf-8') as stdout_file, \
                 open(result.stderr_log_path, 'w', encoding='utf-8') as stderr_file:

                process = subprocess.Popen(
                    [sys.executable, str(script_path)],
                    stdout=stdout_file,
                    stderr=stderr_file,
                    cwd=str(self.workspace_root),
                    text=True,
                    bufsize=1
                )

                # Monitor execution with timeout
                try:
                    return_code = process.wait(timeout=phase_config["timeout"])
                    result.return_code = return_code
                    result.success = (return_code == 0)

                except subprocess.TimeoutExpired:
                    process.kill()
                    result.return_code = -1
                    result.success = False
                    result.errors.append(f"Phase execution timed out after {phase_config['timeout']} seconds")

            result.end_time = datetime.now()

            # Log execution results
            duration = (result.end_time - result.start_time).total_seconds()

            if result.success:
                self.logger.info(f"[SUCCESS] {phase_config['name']} completed in {duration:.1f}s")
            else:
                self.logger.error(f"[ERROR] {phase_config['name']} failed (code: {result.return_code})")

            # Read and log stderr if there were errors
            if result.return_code != 0:
                try:
                    with open(result.stderr_log_path, 'r', encoding='utf-8') as f:
                        stderr_content = f.read()
                        if stderr_content.strip():
                            self.logger.error(f"[ERROR OUTPUT] {stderr_content[:500]}...")
                except:
                    pass

            # Store execution record in database
            self._store_execution_record(result)

            return result

        except Exception as e:
            result.end_time = datetime.now()
            result.success = False
            result.errors.append(str(e))
            self.logger.error(f"[ERROR] Phase execution failed: {e}")
            return result

    def _store_execution_record(self, result: PhaseExecutionResult):
        """Store phase execution record in database"""
        try:
            with sqlite3.connect(self.production_db) as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    INSERT INTO phase_executions
                    (execution_id, phase_id, script_path, start_time, end_time,
                     status, return_code, stdout_log_path, stderr_log_path,
                     script_hash, metrics)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    self.execution_id,
                    result.phase_id,
                    self.phases[result.phase_id]["script"],
                    result.start_time.isoformat(),
                    result.end_time.isoformat() if result.end_time else None,
                    "SUCCESS" if result.success else "FAILED",
                    result.return_code,
                    result.stdout_log_path,
                    result.stderr_log_path,
                    result.database_script_hash,
                    json.dumps(result.metrics)
                ))

                conn.commit()

            self.logger.info(f"[DATABASE] Execution record stored for {result.phase_id}")

        except Exception as e:
            self.logger.error(f"[ERROR] Failed to store execution record: {e}")

    def execute_all_phases(self) -> Dict[str, PhaseExecutionResult]:
        """Execute all phases with comprehensive logging and database storage"""
        self.logger.info("[START] Enterprise Phase Execution Sequence Initiated")
        self.logger.info(f"Execution ID: {self.execution_id}")
        self.logger.info(f"Total Phases: {len(self.phases)}")

        results = {}
        overall_start = datetime.now()

        for phase_id in ["phase3", "phase4", "phase5"]:
            self.logger.info(f"[PHASE] Starting {phase_id}")
            result = self.execute_phase_with_logging(phase_id)
            results[phase_id] = result

            # Log phase completion
            status = "SUCCESS" if result.success else "FAILED"
            self.logger.info(f"[COMPLETE] {phase_id}: {status}")

            # Break on failure if configured
            if not result.success:
                self.logger.warning(
                                    f"[WARNING] {phase_id} failed,
                                    continuing to next phase"
                self.logger.warning(f"[WARNING] {ph)

        overall_duration = (datetime.now() - overall_start).total_seconds()

        # Generate execution summary
        successful_phases = sum(1 for r in results.values() if r.success)
        total_phases = len(results)

        self.logger.info("[SUMMARY] Phase Execution Completed")
        self.logger.info(f"Successful Phases: {successful_phases}/{total_phases}")
        self.logger.info(f"Total Duration: {overall_duration:.1f} seconds")
        self.logger.info(f"Database Scripts Stored: {sum(1 for r in results.values() if r.database_script_stored)}")

        # Generate execution report
        self._generate_execution_report(results, overall_duration)

        return results

    def _generate_execution_report(
                                   self,
                                   results: Dict[str,
                                   PhaseExecutionResult],
                                   duration: float)
    def _generate_execution_report(sel)
        """Generate comprehensive execution report"""
        report = {
            "execution_id": self.execution_id,
            "timestamp": datetime.now().isoformat(),
            "total_duration_seconds": duration,
            "phases": {},
            "summary": {
                "total_phases": len(results),
                "successful_phases": sum(1 for r in results.values() if r.success),
                "failed_phases": sum(1 for r in results.values() if not r.success),
                "database_storage_success_rate": sum(1 for r in results.values() if r.database_script_stored) / len(results) * 100,
                "logs_generated": []
            }
        }

        for phase_id, result in results.items():
            phase_duration = 0
            if result.end_time:
                phase_duration = (result.end_time - result.start_time).total_seconds()

            report["phases"][phase_id] = {
                "name": self.phases[phase_id]["name"],
                "success": result.success,
                "return_code": result.return_code,
                "duration_seconds": phase_duration,
                "database_stored": result.database_script_stored,
                "script_hash": result.database_script_hash,
                "stdout_log": result.stdout_log_path,
                "stderr_log": result.stderr_log_path,
                "errors": result.errors
            }

            # Collect log files
            if result.stdout_log_path:
                report["summary"]["logs_generated"].append(result.stdout_log_path)
            if result.stderr_log_path:
                report["summary"]["logs_generated"].append(result.stderr_log_path)

        # Save report
        report_file = self.logs_dir / f"execution_report_{self.execution_id}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)

        self.logger.info(f"[REPORT] Execution report saved: {report_file}")



        return report


def main():
    """Main execution function with comprehensive error handling"""
    try:
        print("="*80)
        print("ENTERPRISE PHASE DATABASE EXECUTOR")
        print("="*80)
        print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        executor = EnterprisePhaseDatabaseExecutor()
        results = executor.execute_all_phases()

        print()
        print("="*80)
        print("EXECUTION COMPLETED")
        print("="*80)

        for phase_id, result in results.items():
            status = "SUCCESS" if result.success else "FAILED"
            print(f"{phase_id}: {status}")

        return 0 if all(r.success for r in results.values()) else 1

    except Exception as e:
        print(f"[CRITICAL ERROR] Executor failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
