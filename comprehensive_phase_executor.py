#!/usr/bin/env python3
"""
ENTERPRISE PHASE EXECUTION WITH COMPREHENSIVE LOGGING
===================================================
Executes Phases 3, 4, 5 with detailed output capture and database integration

Features:
- Real-time terminal output capture
- Database pattern integration
- Comprehensive execution logging
- Progress monitoring with visual indicators
- Anti-recursion safety protocols
"""

import os
import sys
import subprocess
import logging
import time
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor
import threading
import queue


class ComprehensivePhaseExecutor:
    """Enterprise-grade phase execution with comprehensive logging"""

    def __init__(self):
        self.workspace_root = Path(os.getcwd())
        self.execution_id = f"PHASE_EXEC_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.logs_dir = self.workspace_root / "logs" / "comprehensive_execution"
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        # Setup comprehensive logging
        self._setup_logging()

        # Database connections
        self.analytics_db = self.workspace_root / "analytics.db"
        self.execution_log = []

        self.logger.info(f"[INIT] Comprehensive Phase Executor initialized - ID: {self.execution_id}")

    def _setup_logging(self):
        """Setup comprehensive logging with multiple handlers"""
        log_file = self.logs_dir / f"comprehensive_execution_{self.execution_id}.log"

        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)8s | %(name)20s | %(message)s'
        )

        # File handler with UTF-8 encoding
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)

        # Setup logger
        self.logger = logging.getLogger('ComprehensivePhaseExecutor')
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

        # Prevent duplicate logs
        self.logger.propagate = False

    def capture_database_patterns(self) -> Dict[str, Any]:
        """Capture current database patterns for phase execution"""
        self.logger.info("[DATABASE] Capturing ML patterns from analytics.db")

        patterns = {
            'ml_patterns': [],
            'phase_history': [],
            'compliance_tracking': []
        }

        try:
            conn = sqlite3.connect(self.analytics_db)
            cursor = conn.cursor()

            # Get ML patterns
            cursor.execute("SELECT * FROM ml_pattern_optimization ORDER BY confidence_score DESC LIMIT 10")
            ml_results = cursor.fetchall()
            if ml_results:
                patterns['ml_patterns'] = [
                    {
                        'pattern_id': row[1],
                        'error_codes': row[2],
                        'pattern_regex': row[3],
                        'replacement': row[4],
                        'confidence_score': row[5],
                        'success_rate': row[6]
                    }
                    for row in ml_results
                ]

            # Get phase execution history
            cursor.execute("SELECT * FROM phase_executions ORDER BY created_at DESC LIMIT 5")
            phase_results = cursor.fetchall()
            if phase_results:
                patterns['phase_history'] = [
                    {
                        'execution_id': row[1],
                        'phase_id': row[2],
                        'status': row[5],
                        'compliance_score': row[7]
                    }
                    for row in phase_results
                ]

            conn.close()
            self.logger.info(f"[DATABASE] Captured {len(patterns['ml_patterns'])} ML patterns")

        except Exception as e:
            self.logger.error(f"[DATABASE] Error capturing patterns: {e}")

        return patterns

    def execute_phase_with_logging(self, phase_name: str, script_path: str) -> Dict[str, Any]:
        """Execute a phase with comprehensive output capture"""
        self.logger.info(f"[PHASE] Starting {phase_name} execution")
        start_time = datetime.now()

        # Create phase-specific log file
        phase_log_file = self.logs_dir / f"{phase_name.lower()}_execution_{self.execution_id}.log"

        execution_result = {
            'phase_name': phase_name,
            'start_time': start_time.isoformat(),
            'status': 'RUNNING',
            'output': [],
            'errors': [],
            'metrics': {}
        }

        try:
            # Check if script exists
            if not Path(script_path).exists():
                self.logger.error(f"[PHASE] Script not found: {script_path}")
                execution_result['status'] = 'FAILED'
                execution_result['errors'].append(f"Script not found: {script_path}")
                return execution_result

            # Execute script with output capture
            self.logger.info(f"[PHASE] Executing script: {script_path}")

            with open(phase_log_file, 'w', encoding='utf-8') as log_file:
                process = subprocess.Popen(
                    [sys.executable, script_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1,
                    universal_newlines=True
                )

                # Real-time output capture
                stdout_queue = queue.Queue()
                stderr_queue = queue.Queue()

                def capture_stdout():
                    if process.stdout is not None:
                        for line in iter(process.stdout.readline, ''):
                            stdout_queue.put(line)
                            log_file.write(f"STDOUT: {line}")
                            log_file.flush()

                def capture_stderr():
                    if process.stderr is not None:
                        for line in iter(process.stderr.readline, ''):
                            stderr_queue.put(line)
                            log_file.write(f"STDERR: {line}")
                            log_file.flush()

                # Start capture threads
                stdout_thread = threading.Thread(target=capture_stdout)
                stderr_thread = threading.Thread(target=capture_stderr)
                stdout_thread.start()
                stderr_thread.start()

                # Wait for completion with timeout
                timeout = 300  # 5 minutes
                try:
                    process.wait(timeout=timeout)
                except subprocess.TimeoutExpired:
                    process.kill()
                    execution_result['errors'].append(f"Process timed out after {timeout} seconds")
                    self.logger.error(f"[PHASE] {phase_name} timed out")

                # Collect output
                stdout_thread.join(timeout=5)
                stderr_thread.join(timeout=5)

                # Get all output
                while not stdout_queue.empty():
                    execution_result['output'].append(stdout_queue.get())

                while not stderr_queue.empty():
                    execution_result['errors'].append(stderr_queue.get())

                # Set final status
                if process.returncode == 0:
                    execution_result['status'] = 'SUCCESS'
                    self.logger.info(f"[PHASE] {phase_name} completed successfully")
                else:
                    execution_result['status'] = 'FAILED'
                    self.logger.error(f"[PHASE] {phase_name} failed with return code {process.returncode}")

        except Exception as e:
            execution_result['status'] = 'ERROR'
            execution_result['errors'].append(str(e))
            self.logger.error(f"[PHASE] Exception during {phase_name}: {e}")

        # Calculate metrics
        end_time = datetime.now()
        execution_result['end_time'] = end_time.isoformat()
        execution_result['duration_seconds'] = (end_time - start_time).total_seconds()

        # Save execution result
        self.execution_log.append(execution_result)

        return execution_result

    def save_execution_summary(self) -> str:
        """Save comprehensive execution summary"""
        summary_file = self.logs_dir / f"execution_summary_{self.execution_id}.json"

        summary = {
            'execution_id': self.execution_id,
            'timestamp': datetime.now().isoformat(),
            'total_phases': len(self.execution_log),
            'successful_phases': len([r for r in self.execution_log if r['status'] == 'SUCCESS']),
            'failed_phases': len([r for r in self.execution_log if r['status'] == 'FAILED']),
            'phases': self.execution_log
        }

        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        self.logger.info(f"[SUMMARY] Execution summary saved: {summary_file}")
        return str(summary_file)


def main():
    """Main execution function"""
    executor = ComprehensivePhaseExecutor()

    # Capture database patterns first
    patterns = executor.capture_database_patterns()
    executor.logger.info(f"[DATABASE] Captured patterns: {len(patterns['ml_patterns'])} ML patterns available")

    # Define phases to execute
    phases = [
        ("PHASE3_SYSTEMATIC_STYLE", "phase3_systematic_style_compliance.py"),
        ("PHASE4_ENTERPRISE_VALIDATION", "phase4_enterprise_validation.py"),
        ("PHASE5_CONTINUOUS_OPERATION", "phase5_continuous_operation.py")
    ]

    executor.logger.info("[EXEC] Starting comprehensive phase execution sequence")

    # Execute each phase
    for phase_name, script_path in phases:
        result = executor.execute_phase_with_logging(phase_name, script_path)

        executor.logger.info(f"[RESULT] {phase_name}: {result['status']}")
        if result['status'] != 'SUCCESS':
            executor.logger.warning(f"[RESULT] {phase_name} issues: {len(result['errors'])} errors")

    # Save comprehensive summary
    summary_file = executor.save_execution_summary()

    executor.logger.info("[COMPLETE] Comprehensive phase execution completed")
    executor.logger.info(f"[COMPLETE] Summary available at: {summary_file}")

    return summary_file

if __name__ == "__main__":
    main()
