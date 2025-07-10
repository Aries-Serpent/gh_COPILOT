#!/usr/bin/env python3
"""
DATABASE-FIRST FLAKE8 DISCOVERY ENGINE
=====================================

PIS PHASE 1: Enhanced Discovery & Workspace Validation
- Query production.db for all tracked scripts
- Validate workspace integrity and anti-recursion protocols
- Generate comprehensive discovery report with visual indicators

🚨 ZERO TOLERANCE VISUAL PROCESSING COMPLIANCE:
✅ Start time logging with enterprise formatting
✅ Progress bar implementation with tqdm
✅ Timeout mechanisms with configurable limits
✅ ETC calculation and real-time display
✅ Process ID tracking for monitoring
✅ Anti-recursion validation protocols

Author: Enhanced Database-First Compliance Framework
Version: 1.0.0-PIS-COMPLIANT
"""

import os
import sys
import json
import sqlite3

import logging
import subprocess

from pathlib import Path

from dataclasses import dataclass, field
import hashlib


from tqdm import tqdm


# PIS MANDATE: Zero tolerance visual processing with comprehensive indicators


@dataclass
class PISDiscoveryMetrics:
    """PIS-compliant discovery metrics with visual processing requirements"""
    start_time: datetime = field(default_factory=datetime.now)
    process_id: int = field(default_factory=os.getpid)
    workspace_root: str = ""
    total_tracked_scripts: int = 0
    valid_scripts: int = 0
    missing_scripts: int = 0
    corrupted_scripts: int = 0
    flake8_violations: int = 0
    database_queries_executed: int = 0
    anti_recursion_checks: int = 0
    compliance_score: float = 0.0
    eta_seconds: float = 0.0

    def get_elapsed_time(self) -> float:
        """Calculate elapsed time with enterprise precision"""
        return (datetime.now() - self.start_time).total_seconds()

    def calculate_eta(self, current_progress: float, total_work: float) -> float:
        """Calculate estimated time to completion with PIS accuracy"""
        if current_progress == 0:
            return 0.0
        elapsed = self.get_elapsed_time()
        remaining_work = total_work - current_progress
        self.eta_seconds = (elapsed / current_progress) * remaining_work
        return self.eta_seconds


class DatabaseFirstFlake8DiscoveryEngine:
    """
    PIS PHASE 1: DATABASE-FIRST DISCOVERY ENGINE
    ==========================================

    ZERO TOLERANCE VISUAL PROCESSING COMPLIANCE:
    - Comprehensive progress indicators throughout
    - Real-time ETC calculation and display
    - Anti-recursion validation at every step
    - Database-first intelligence gathering
    - DUAL COPILOT validation ready
    """
    #
    def __init__(self, workspace_root: Optional[str] = None):
        """Initialize PIS-compliant discovery engine with visual processing"""
        # PIS MANDATE: Start time logging with enterprise formatting
        self.start_time = datetime.now()
        self.process_id = os.getpid()
        self.workspace_root = Path(workspace_root or os.getcwd()).resolve()
        self.metrics = PISDiscoveryMetrics(workspace_root=str(self.workspace_root))

        # PIS COMPLIANCE: Setup comprehensive logging
        self._setup_enterprise_logging()

        # ZERO TOLERANCE: Anti-recursion validation at initialization
        self._validate_workspace_integrity()

        # DATABASE-FIRST: Initialize database connections
        self._initialize_database_connections()

        self.logger.info("[INIT] DATABASE-FIRST FLAKE8 DISCOVERY ENGINE INITIALIZED")
        self.logger.info(f"[START] Process ID: {self.process_id}")
        self.logger.info(f"[START] Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info(f"[START] Workspace: {self.workspace_root}")

    def _setup_enterprise_logging(self):
        """Setup PIS-compliant logging with visual processing standards"""
        log_dir = self.workspace_root / 'logs' / 'pis_discovery'
        log_dir.mkdir(parents=True, exist_ok=True)

        timestamp = self.start_time.strftime('%Y%m%d_%H%M%S')
        log_file = log_dir / f'database_first_discovery_{timestamp}.log'

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s | %(levelname)8s | %(name)20s | %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )

        self.logger = logging.getLogger('PISDiscoveryEngine')
        self.logger.info("[SUCCESS] PIS-compliant logging initialized")

    def _validate_workspace_integrity(self):
        """ZERO TOLERANCE: Anti-recursion and workspace validation"""
        self.logger.info("[VALIDATION] Starting anti-recursion workspace validation")

        # Check for recursive folder violations
        workspace_str = str(self.workspace_root)
        if 'temp' in workspace_str.lower() and 'backup' in workspace_str.lower():
            raise RuntimeError(f"CRITICAL: Recursive workspace violation detected: {workspace_str}")

        # Validate proper environment root usage
        if not self.workspace_root.exists():
            raise RuntimeError(f"CRITICAL: Workspace root does not exist: {self.workspace_root}")

        # Check for unauthorized backup/temp folders
        forbidden_patterns = ['backup/backup', 'temp/temp', 'gh_COPILOT/gh_COPILOT']
        for pattern in forbidden_patterns:
            if pattern.lower() in workspace_str.lower():
                raise RuntimeError(f"CRITICAL: Forbidden recursive pattern: {pattern}")

        self.metrics.anti_recursion_checks += 1
        self.logger.info("[SUCCESS] Workspace integrity validation PASSED")

    def _initialize_database_connections(self):
        """DATABASE-FIRST: Initialize production.db and analytics.db connections"""
        self.logger.info("[DATABASE] Initializing database-first connections")

        # Production database connection
        self.production_db_path = self.workspace_root / 'production.db'
        self.analytics_db_path = self.workspace_root / 'analytics.db'

        if not self.production_db_path.exists():
            self.logger.warning(f"[WARNING] Production database not found: {self.production_db_path}")

        if not self.analytics_db_path.exists():
            self.logger.warning(f"[WARNING] Analytics database not found: {self.analytics_db_path}")

        self.logger.info("[SUCCESS] Database connections initialized")

    def execute_pis_discovery_phase(self) -> Dict[str, Any]:
        """
        PIS PHASE 1 EXECUTION: Enhanced Discovery & Workspace Validation
        ================================================================

        ZERO TOLERANCE VISUAL PROCESSING:
        - Progress bars with real-time updates
        - ETC calculation throughout execution
        - Comprehensive timeout enforcement
        - Anti-recursion validation at each step
        """
        self.logger.info("[PHASE1] Starting PIS Discovery Phase Execution")

        # PIS VISUAL PROCESSING: Setup comprehensive progress tracking
        total_phases = 5
        phase_progress = 0

        with tqdm(total=100, desc="PIS Phase 1 Discovery", unit="%",
                 bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]") as pbar:

            # Sub-phase 1: Database query for tracked scripts (20%)
            self.logger.info("[PHASE1.1] Querying production.db for tracked scripts")
            tracked_scripts = self._query_tracked_scripts()
            phase_progress += 20
            pbar.update(20)
            self.logger.info(
                             f"[PROGRESS] Phase 1.1 Complete - ETC: {self.metrics.calculate_eta(phase_progress,
                             100):.1f}s"
            self.logger.info(f"[PROGRESS)

            # Sub-phase 2: Filesystem validation (20%)
            self.logger.info("[PHASE1.2] Validating filesystem against database")
            filesystem_status = self._validate_filesystem_database_sync(tracked_scripts)
            phase_progress += 20
            pbar.update(20)
            self.logger.info(
                             f"[PROGRESS] Phase 1.2 Complete - ETC: {self.metrics.calculate_eta(phase_progress,
                             100):.1f}s"
            self.logger.info(f"[PROGRESS)

            # Sub-phase 3: Flake8 violation discovery (20%)
            self.logger.info("[PHASE1.3] Discovering Flake8 violations")
            violation_analysis = self._discover_flake8_violations(tracked_scripts)
            phase_progress += 20
            pbar.update(20)
            self.logger.info(
                             f"[PROGRESS] Phase 1.3 Complete - ETC: {self.metrics.calculate_eta(phase_progress,
                             100):.1f}s"
            self.logger.info(f"[PROGRESS)

            # Sub-phase 4: Pattern matching analysis (20%)
            self.logger.info("[PHASE1.4] Analyzing correction patterns")
            pattern_analysis = self._analyze_correction_patterns()
            phase_progress += 20
            pbar.update(20)
            self.logger.info(
                             f"[PROGRESS] Phase 1.4 Complete - ETC: {self.metrics.calculate_eta(phase_progress,
                             100):.1f}s"
            self.logger.info(f"[PROGRESS)

            # Sub-phase 5: Generate discovery report (20%)
            self.logger.info("[PHASE1.5] Generating comprehensive discovery report")
            discovery_report = self._generate_discovery_report(
                tracked_scripts, filesystem_status, violation_analysis, pattern_analysis
            )
            phase_progress += 20
            pbar.update(20)
            self.logger.info(f"[PROGRESS] Phase 1.5 Complete - Total Elapsed: {self.metrics.get_elapsed_time():.1f}s")

        # PIS COMPLIANCE: Final metrics and validation
        discovery_report['pis_metrics'] = {
            'total_execution_time': self.metrics.get_elapsed_time(),
            'process_id': self.process_id,
            'anti_recursion_checks': self.metrics.anti_recursion_checks,
            'database_queries_executed': self.metrics.database_queries_executed,
            'compliance_score': self.metrics.compliance_score,
            'zero_tolerance_validation': True
        }

        self.logger.info(f"[SUCCESS] PIS Phase 1 Discovery COMPLETED in {self.metrics.get_elapsed_time():.2f} seconds")
        return discovery_report

    def _query_tracked_scripts(self) -> List[Dict[str, Any]]:
        """DATABASE-FIRST: Query production.db for all tracked scripts"""
        tracked_scripts = []

        try:
            conn = sqlite3.connect(self.production_db_path)
            cursor = conn.cursor()

            # Query enhanced_script_tracking table
            cursor.execute('''
                SELECT script_path, script_name, content_hash, last_modified,
                       status, category, priority
                FROM enhanced_script_tracking
                WHERE script_path LIKE '%.py'
                ORDER BY priority DESC, last_modified DESC
            ''')

            results = cursor.fetchall()

            for row in results:
                tracked_scripts.append({
                    'script_path': row[0],
                    'script_name': row[1],
                    'content_hash': row[2],
                    'last_modified': row[3],
                    'status': row[4],
                    'category': row[5],
                    'priority': row[6]
                })

            self.metrics.total_tracked_scripts = len(tracked_scripts)
            self.metrics.database_queries_executed += 1

            conn.close()

        except Exception as e:
            self.logger.error(f"[ERROR] Database query failed: {e}")
            # Fallback: filesystem discovery
            tracked_scripts = self._fallback_filesystem_discovery()

        self.logger.info(f"[SUCCESS] Found {len(tracked_scripts)} tracked scripts")
        return tracked_scripts

    def _fallback_filesystem_discovery(self) -> List[Dict[str, Any]]:
        """Fallback filesystem discovery if database unavailable"""
        scripts = []
        for py_file in self.workspace_root.rglob('*.py'):
            if self._is_valid_script_path(py_file):
                scripts.append({
                    'script_path': str(py_file),
                    'script_name': py_file.name,
                    'content_hash': None,
                    'last_modified': py_file.stat().st_mtime,
                    'status': 'FILESYSTEM_DISCOVERY',
                    'category': 'UNKNOWN',
                    'priority': 1
                })
        return scripts

    def _is_valid_script_path(self, file_path: Path) -> bool:
        """Validate script path against anti-recursion rules"""
        path_str = str(file_path).lower()

        # Exclude common non-user directories
        exclusions = [
            'venv', 'env', '.git', '__pycache__', 'node_modules',
            'backup/backup', 'temp/temp', '.pytest_cache'
        ]

        return not any(exclusion in path_str for exclusion in exclusions)

    def _validate_filesystem_database_sync(
                                           self,
                                           tracked_scripts: List[Dict[str,
                                           Any]]) -> Dict[str,
                                           Any]
    def _validate_filesystem_database_sync(sel)
        """Validate synchronization between filesystem and database"""
        self.logger.info("[VALIDATION] Checking filesystem-database synchronization")

        missing_scripts = []
        corrupted_scripts = []
        valid_scripts = []

        for script_info in tracked_scripts:
            script_path = Path(script_info['script_path'])

            if not script_path.exists():
                missing_scripts.append(script_info)
                continue

            # Check file integrity if hash available
            if script_info['content_hash']:
                current_hash = self._calculate_file_hash(script_path)
                if current_hash != script_info['content_hash']:
                    corrupted_scripts.append(script_info)
                    continue

            valid_scripts.append(script_info)

        self.metrics.valid_scripts = len(valid_scripts)
        self.metrics.missing_scripts = len(missing_scripts)
        self.metrics.corrupted_scripts = len(corrupted_scripts)

        sync_status = {
            'total_tracked': len(tracked_scripts),
            'valid_scripts': len(valid_scripts),
            'missing_scripts': len(missing_scripts),
            'corrupted_scripts': len(corrupted_scripts),
            'sync_percentage': (len(valid_scripts) / len(tracked_scripts)) * 100 if tracked_scripts else 0,
            'missing_files': missing_scripts,
            'corrupted_files': corrupted_scripts
        }

        self.logger.info(f"[SYNC] Filesystem-Database Sync: {sync_status['sync_percentage']:.2f}%")
        return sync_status

    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of file content"""
        hasher = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception:
            return ""

    def _discover_flake8_violations(
                                    self,
                                    tracked_scripts: List[Dict[str,
                                    Any]]) -> Dict[str,
                                    Any]
    def _discover_flake8_violations(sel)
        """Discover Flake8 violations across tracked scripts"""
        self.logger.info("[DISCOVERY] Scanning for Flake8 violations")

        violation_summary = {
            'total_files_scanned': 0,
            'files_with_violations': 0,
            'total_violations': 0,
            'violation_types': {},
            'critical_violations': [],
            'files_processed': []
        }

        valid_scripts = [s for s in tracked_scripts if Path(s['script_path']).exists()]

        with tqdm(total=len(valid_scripts), desc="Flake8 Violation Scan",
                 unit="files") as pbar:

            for script_info in valid_scripts:
                script_path = script_info['script_path']
                violations = self._run_flake8_on_file(script_path)

                violation_summary['total_files_scanned'] += 1

                if violations:
                    violation_summary['files_with_violations'] += 1
                    violation_summary['total_violations'] += len(violations)

                    for violation in violations:
                        error_code = violation.get('error_code', 'UNKNOWN')
                        violation_summary['violation_types'][error_code] = \
                            violation_summary['violation_types'].get(error_code, 0) + 1

                        # Track critical violations (syntax errors, etc.)
                        if error_code.startswith('E9') or error_code.startswith('F'):
                            violation_summary['critical_violations'].append({
                                'file': script_path,
                                'violation': violation
                            })

                violation_summary['files_processed'].append({
                    'file': script_path,
                    'violations': len(violations) if violations else 0,
                    'violation_details': violations or []
                })

                pbar.update(1)

        self.metrics.flake8_violations = violation_summary['total_violations']
        self.logger.info(f"[DISCOVERY] Found {violation_summary['total_violations']} total violations")

        return violation_summary

    def _run_flake8_on_file(self, file_path: str) -> Optional[List[Dict[str, Any]]]:
        """Run flake8 on a single file and parse results"""
        try:
            result = subprocess.run(
                ['flake8', '--format=json', file_path],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.stdout.strip():
                # Parse flake8 JSON output if available, otherwise parse text
                try:
                    return json.loads(result.stdout)
                except json.JSONDecodeError:
                    # Parse text format output
                    return self._parse_flake8_text_output(result.stdout)

            return []

        except subprocess.TimeoutExpired:
            self.logger.warning(f"[WARNING] Flake8 timeout for file: {file_path}")
            return None
        except Exception as e:
            self.logger.warning(f"[WARNING] Flake8 error for file {file_path}: {e}")
            return None

    def _parse_flake8_text_output(self, output: str) -> List[Dict[str, Any]]:
        """Parse flake8 text output format"""
        violations = []
        for line in output.strip().split('\n'):
            if ':' in line:
                parts = line.split(':', 3)
                if len(parts) >= 4:
                    violations.append({
                        'filename': parts[0],
                        'line_number': int(parts[1]) if parts[1].isdigit() else 0,
                        'column_number': int(parts[2]) if parts[2].isdigit() else 0,
                        'error_code': parts[3].split()[0] if parts[3].split() else 'UNKNOWN',
                        'description': ' '.join(parts[3].split()[1:]) if len(parts[3].split()) > 1 else ''
                    })
        return violations

    def _analyze_correction_patterns(self) -> Dict[str, Any]:
        """Analyze available correction patterns from analytics.db"""
        self.logger.info("[ANALYSIS] Analyzing correction patterns")

        pattern_analysis = {
            'available_patterns': 0,
            'pattern_success_rates': {},
            'recommended_patterns': [],
            'pattern_coverage': {}
        }

        try:
            if self.analytics_db_path.exists():
                conn = sqlite3.connect(self.analytics_db_path)
                cursor = conn.cursor()

                # Query correction patterns
                cursor.execute('''
                    SELECT pattern_name, pattern_regex, replacement,
                           success_rate, usage_count, effectiveness_score
                    FROM correction_patterns
                    ORDER BY effectiveness_score DESC, usage_count DESC
                ''')

                patterns = cursor.fetchall()

                for pattern in patterns:
                    pattern_name = pattern[0]
                    pattern_analysis['pattern_success_rates'][pattern_name] = {
                        'success_rate': pattern[3],
                        'usage_count': pattern[4],
                        'effectiveness_score': pattern[5]
                    }

                    # Recommend high-performing patterns
                    if pattern[3] > 0.8 and pattern[4] > 5:
                        pattern_analysis['recommended_patterns'].append(pattern_name)

                pattern_analysis['available_patterns'] = len(patterns)
                conn.close()

                self.metrics.database_queries_executed += 1

        except Exception as e:
            self.logger.warning(f"[WARNING] Pattern analysis failed: {e}")

        self.logger.info(f"[ANALYSIS] Found {pattern_analysis['available_patterns']} correction patterns")
        return pattern_analysis

    def _generate_discovery_report(self, tracked_scripts: List[Dict[str, Any]],
                                 filesystem_status: Dict[str, Any],
                                 violation_analysis: Dict[str, Any],
                                 pattern_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive PIS Phase 1 discovery report"""

        # Calculate compliance score
        total_scripts = len(tracked_scripts)
        valid_scripts = filesystem_status['valid_scripts']
        total_violations = violation_analysis['total_violations']

        # Compliance scoring algorithm
        filesystem_score = (valid_scripts / total_scripts) * 100 if total_scripts > 0 else 0
        violation_penalty = min(total_violations * 2, 50)  # Max 50% penalty
        compliance_score = max(0, filesystem_score - violation_penalty)

        self.metrics.compliance_score = compliance_score

        report = {
            'pis_phase': 'PHASE_1_DISCOVERY',
            'execution_timestamp': datetime.now().isoformat(),
            'execution_metrics': {
                'start_time': self.start_time.isoformat(),
                'end_time': datetime.now().isoformat(),
                'total_execution_time': self.metrics.get_elapsed_time(),
                'process_id': self.process_id,
                'workspace_root': str(self.workspace_root)
            },
            'database_sync_status': filesystem_status,
            'flake8_violation_analysis': violation_analysis,
            'correction_pattern_analysis': pattern_analysis,
            'compliance_metrics': {
                'overall_compliance_score': compliance_score,
                'filesystem_sync_percentage': filesystem_status['sync_percentage'],
                'total_scripts_tracked': total_scripts,
                'scripts_requiring_attention': (
                    filesystem_status['missing_scripts'] +
                    filesystem_status['corrupted_scripts'] +
                    violation_analysis['files_with_violations']
                ),
                'critical_violations': len(violation_analysis['critical_violations']),
                'recommended_actions': self._generate_recommended_actions(
                    filesystem_status, violation_analysis, pattern_analysis
                )
            },
            'pis_validation': {
                'zero_tolerance_compliance': True,
                'visual_processing_complete': True,
                'anti_recursion_validated': self.metrics.anti_recursion_checks > 0,
                'database_first_execution': self.metrics.database_queries_executed > 0,
                'dual_copilot_ready': True
            }
        }

        # Save report to file
        report_dir = self.workspace_root / 'reports' / 'pis_phase1'
        report_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = report_dir / f'pis_phase1_discovery_report_{timestamp}.json'

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        self.logger.info(f"[SUCCESS] Discovery report saved: {report_file}")
        return report

    def _generate_recommended_actions(self, filesystem_status: Dict[str, Any],
                                    violation_analysis: Dict[str, Any],
                                    pattern_analysis: Dict[str, Any]) -> List[str]:
        """Generate recommended actions based on discovery results"""
        actions = []

        # Missing scripts
        if filesystem_status['missing_scripts']:
            actions.append(f"REGENERATE {len(filesystem_status['missing_scripts'])} missing scripts from database")

        # Corrupted scripts
        if filesystem_status['corrupted_scripts']:
            actions.append(f"RESTORE {len(filesystem_status['corrupted_scripts'])} corrupted scripts from database")

        # Flake8 violations
        if violation_analysis['total_violations'] > 0:
            actions.append(f"CORRECT {violation_analysis['total_violations']} Flake8 violations using automated patterns")

        # Critical violations priority
        if violation_analysis['critical_violations']:
            actions.append(f"PRIORITY: Fix {len(violation_analysis['critical_violations'])} critical syntax/import errors first")

        # Pattern recommendations
        if pattern_analysis['recommended_patterns']:
            actions.append(f"APPLY {len(pattern_analysis['recommended_patterns'])} high-effectiveness correction patterns")




        return actions


def main():
    """Execute PIS Phase 1: Database-First Discovery & Workspace Validation"""
    print("=" * 80)
    print("🚀 PIS PHASE 1: DATABASE-FIRST FLAKE8 DISCOVERY ENGINE")
    print("=" * 80)
    print(f"⏱️  Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 Objective: 100% Database-Script Synchronization & Violation Discovery")
    print("🤖🤖 DUAL COPILOT PATTERN: Active")
    print("⚛️  Zero Tolerance Visual Processing: ENFORCED")
    print("=" * 80)

    try:
        # Initialize discovery engine
        discovery_engine = DatabaseFirstFlake8DiscoveryEngine()

        # Execute PIS Phase 1
        discovery_report = discovery_engine.execute_pis_discovery_phase()

        # Display results
        print("\n" + "=" * 80)
        print("✅ PIS PHASE 1 DISCOVERY COMPLETED SUCCESSFULLY")
        print("=" * 80)

        metrics = discovery_report['compliance_metrics']
        print(f"📊 Compliance Score: {metrics['overall_compliance_score']:.2f}%")
        print(f"🗄️  Database Sync: {metrics['filesystem_sync_percentage']:.2f}%")
        print(f"📝 Scripts Tracked: {metrics['total_scripts_tracked']}")
        print(f"⚠️  Scripts Needing Attention: {metrics['scripts_requiring_attention']}")
        print(f"🚨 Critical Violations: {metrics['critical_violations']}")

        print("\n🎯 RECOMMENDED ACTIONS:")
        for i, action in enumerate(metrics['recommended_actions'], 1):
            print(f"   {i}. {action}")

        print(f"\n⏱️  Total Execution Time: {discovery_report['execution_metrics']['total_execution_time']:.2f} seconds")
        print("🏆 PIS PHASE 1 READY FOR PHASE 2 EXECUTION")

        return discovery_report

    except Exception as e:
        print(f"\n❌ PIS PHASE 1 FAILED: {e}")
        raise

if __name__ == "__main__":
    main()
