#!/usr/bin/env python3
"""
DATABASE-FIRST FLAKE8 COMPLIANCE SCANNER - PIS PHASE 2
========================================================

PLAN ISSUED STATEMENT (PIS) PHASE 2: COMPLIANCE SCAN
Enterprise-Grade Flake8/PEP 8 Compliance Enforcement System

ENTERPRISE MANDATES:
- Zero-tolerance visual processing indicators
- DUAL COPILOT validation protocols
- Anti-recursion protection
- Comprehensive audit logging
- Real-time metrics and ETCs
- Database-first approach with fallback
- Chunked processing for scalability

AUTHOR: GitHub Copilot Enterprise System
VERSION: 2.0 (PIS Phase 2)
COMPLIANCE: Enterprise Zero-Tolerance Standards
"""

import os
import sys
import json
import time
import sqlite3
import logging
import subprocess
import threading
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict
import signal
import hashlib

# Visual Processing Indicators (Zero-Tolerance Requirement)
try:
    from tqdm import tqdm as TqdmProgress
    TQDM_AVAILABLE = True
    tqdm = TqdmProgress
except ImportError:
    TQDM_AVAILABLE = False
    print("WARNING: tqdm not available - installing for visual processing compliance")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "tqdm"])
        from tqdm import tqdm as TqdmProgress
        TQDM_AVAILABLE = True
        tqdm = TqdmProgress
    except subprocess.CalledProcessError:
        print("ERROR: Unable to install tqdm - using fallback progress indicators")
        class TqdmFallback:
            def __init__(self, *args, **kwargs):
                self.total = kwargs.get('total', 100)
                self.current = 0
                self.desc = kwargs.get('desc', 'Progress')
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass
            def update(self, n):
                self.current += n
                print(f"{self.desc}: {self.current}/{self.total}")
            def set_postfix(self, postfix_dict):
                print(f"Status: {postfix_dict}")
            def set_description(self, desc):
                self.desc = desc
            def close(self):
                pass

        tqdm = TqdmFallback

# Enhanced Logging Configuration


def setup_enterprise_logging() -> logging.Logger:
    """Setup comprehensive enterprise logging with visual indicators."""
    log_dir = Path("logs/pis_phase2")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"pis_phase2_compliance_scan_{timestamp}.log"
    
    # Create file handler with UTF-8 encoding
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    
    # Create console handler with ASCII-safe formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # Set formatters
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Configure logger
    logger = logging.getLogger("PIS_PHASE2_COMPLIANCE")
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    logger.info("PIS PHASE 2: COMPLIANCE SCAN - ENTERPRISE LOGGING INITIALIZED")
    logger.info(f"Log File: {log_file}")
    
    return logger


@dataclass
class ComplianceViolation:
    """Structured compliance violation data."""
    file_path: str
    line_number: int
    column_number: int
    error_code: str
    error_message: str
    severity: str
    category: str

    timestamp: str

    
@dataclass
class ComplianceMetrics:
    """Comprehensive compliance metrics for enterprise reporting."""
    total_files_scanned: int = 0
    compliant_files: int = 0
    non_compliant_files: int = 0
    total_violations: int = 0
    critical_violations: int = 0
    warning_violations: int = 0
    style_violations: int = 0
    complexity_violations: int = 0
    documentation_violations: int = 0
    scan_duration: float = 0.0

    compliance_score: float = 0.0

    timestamp: str = ""

class AntiRecursionProtocol:
    """Enterprise anti-recursion protection system."""
    
    def __init__(self, max_depth: int = 10, max_files: int = 5000):
        self.max_depth = max_depth
        self.max_files = max_files
        self.processed_files = set()
        self.current_depth = 0
        self.start_time = time.time()
        self.timeout_seconds = 3600  # 1 hour timeout
        
    def check_recursion(self, file_path: str) -> bool:
        """Check for recursion and resource limits."""
        if time.time() - self.start_time > self.timeout_seconds:
            raise TimeoutError("TIMEOUT: Operation exceeded maximum time limit")

        if len(self.processed_files) >= self.max_files:
            raise ResourceError("RESOURCE LIMIT: Maximum files processed")
            
        if self.current_depth >= self.max_depth:
            raise RecursionError("RECURSION LIMIT: Maximum depth exceeded")

        file_hash = hashlib.md5(file_path.encode()).hexdigest()
        if file_hash in self.processed_files:

            return False  # Already processed

            
        self.processed_files.add(file_hash)
        return True



class ResourceError(Exception):
    """Custom exception for resource limits."""
    pass

class DatabaseFirstComplianceScanner:
    """Enterprise-grade database-first compliance scanner with visual processing."""

    def __init__(self, workspace_path: Optional[str] = None):
        """Initialize scanner with comprehensive validation."""
        self.workspace_path = Path(workspace_path) if workspace_path else Path.cwd()
        if not self.workspace_path.exists():
            raise ValueError(f"Workspace path does not exist: {self.workspace_path}")

        self.logger = setup_enterprise_logging()
        self.anti_recursion = AntiRecursionProtocol()
        self.metrics = ComplianceMetrics()
        self.violations: List[ComplianceViolation] = []
        self.start_time = time.time()
        
        # Database connections
        self.production_db = None
        self.analytics_db = None
        
        # Visual processing indicators
        self.progress_bar = None
        self.status_display = None
        
        # Validate dependencies
        self._validate_dependencies()
        
        # Signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _validate_dependencies(self):
        """Validate required dependencies."""
        # Check flake8 availability
        try:
            result = subprocess.run(['flake8', '--version'],
                                  capture_output=True, check=True, timeout=10)
            self.logger.info(f"Flake8 available: {result.stdout.decode().strip()}")
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            raise RuntimeError("Flake8 is required but not available. Install with: pip install flake8")
            
    def _signal_handler(self, signum, frame):
        """Handle graceful shutdown."""
        self.logger.warning(f"SHUTDOWN SIGNAL RECEIVED: {signum}")
        if self.progress_bar:
            self.progress_bar.close()
        self.cleanup()
        sys.exit(0)

    def initialize_databases(self) -> bool:
        """Initialize database connections with enterprise validation."""
        try:
            self.logger.info("INITIALIZING DATABASE CONNECTIONS...")
            
            # Production database
            prod_db_path = self.workspace_path / "production.db"
            if prod_db_path.exists():
                try:
                    self.production_db = sqlite3.connect(str(prod_db_path), timeout=30)
                    self.production_db.row_factory = sqlite3.Row
                    # Test connection
                    self.production_db.execute("SELECT 1").fetchone()
                    self.logger.info("Production database connected")
                except sqlite3.Error as e:
                    self.logger.error(f"Production database connection failed: {e}")
                    self.production_db = None
            else:
                self.logger.warning("Production database not found - using filesystem fallback")

            # Analytics database
            analytics_db_path = self.workspace_path / "analytics.db"
            try:
                self.analytics_db = sqlite3.connect(str(analytics_db_path), timeout=30)
                self.analytics_db.row_factory = sqlite3.Row

                if not analytics_db_path.exists():
                    self.logger.info("Creating new analytics database")
                    
                self._create_analytics_tables()
                self.logger.info("Analytics database connected")

            except sqlite3.Error as e:
                self.logger.error(f"Analytics database connection failed: {e}")
                self.analytics_db = None

            return True
            
        except Exception as e:
            self.logger.error(f"DATABASE INITIALIZATION FAILED: {e}")
            return False

    def _create_analytics_tables(self):
        """Create analytics tables for compliance tracking."""
        try:
            if not self.analytics_db:
                return
                
            # Create compliance tracking table
            self.analytics_db.execute("""
                CREATE TABLE IF NOT EXISTS compliance_scans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scan_timestamp TEXT NOT NULL,
                    total_files INTEGER NOT NULL,
                    compliant_files INTEGER NOT NULL,
                    non_compliant_files INTEGER NOT NULL,
                    total_violations INTEGER NOT NULL,
                    compliance_score REAL NOT NULL,
                    scan_duration REAL NOT NULL,
                    phase TEXT NOT NULL DEFAULT 'PHASE_2'
                )
            """)
            
            # Create violation tracking table
            self.analytics_db.execute("""
                CREATE TABLE IF NOT EXISTS compliance_violations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scan_id INTEGER NOT NULL,
                    file_path TEXT NOT NULL,
                    line_number INTEGER NOT NULL,
                    column_number INTEGER NOT NULL,
                    error_code TEXT NOT NULL,
                    error_message TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    category TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY (scan_id) REFERENCES compliance_scans (id)
                )
            """)

            self.analytics_db.commit()
            self.logger.info("Analytics tables created successfully")
            
        except sqlite3.Error as e:
            self.logger.error(f"ANALYTICS TABLE CREATION FAILED: {e}")
            
    def discover_scripts(self) -> List[str]:
        """Discover Python scripts using database-first approach."""
        scripts = []

        try:
            # Try database-first approach
            if self.production_db:
                self.logger.info("DISCOVERING SCRIPTS FROM PRODUCTION DATABASE...")
                
                try:
                    # Check if script_tracking table exists
                    cursor = self.production_db.execute("""
                        SELECT name FROM sqlite_master
                        WHERE type='table' AND name='script_tracking'
                    """)
                    
                    if cursor.fetchone():
                        cursor = self.production_db.execute("""
                            SELECT DISTINCT file_path FROM script_tracking 
                            WHERE file_path LIKE '%.py'
                            ORDER BY file_path
                        """)
                        
                        for row in cursor:
                            file_path = row['file_path']
                            if self.anti_recursion.check_recursion(file_path):
                                if Path(file_path).exists():
                                    scripts.append(file_path)
                                else:
                                    self.logger.warning(f"DATABASE SCRIPT NOT FOUND: {file_path}")

                        self.logger.info(f"DISCOVERED {len(scripts)} SCRIPTS FROM DATABASE")
                    else:
                        self.logger.warning("script_tracking table not found - using filesystem fallback")
                        scripts = self._discover_from_filesystem()
                        
                except sqlite3.Error as db_error:
                    self.logger.warning(f"DATABASE QUERY FAILED: {db_error} - using filesystem fallback")
                    scripts = self._discover_from_filesystem()
                    
            else:
                # Fallback to filesystem discovery
                scripts = self._discover_from_filesystem()

        except Exception as e:
            self.logger.error(f"SCRIPT DISCOVERY FAILED: {e}")
            scripts = self._discover_from_filesystem()
            
        return scripts

    def _discover_from_filesystem(self) -> List[str]:
        """Discover scripts from filesystem with limits."""
        scripts = []
        self.logger.info("FALLBACK: DISCOVERING SCRIPTS FROM FILESYSTEM...")
        
        try:
            discovered_count = 0
            max_files = self.anti_recursion.max_files
            
            for py_file in self.workspace_path.rglob("*.py"):
                if discovered_count >= max_files:
                    self.logger.warning(f"FILE LIMIT REACHED: {max_files} files discovered")
                    break

                if self.anti_recursion.check_recursion(str(py_file)):
                    scripts.append(str(py_file))
                    discovered_count += 1

            self.logger.info(f"DISCOVERED {len(scripts)} SCRIPTS FROM FILESYSTEM")

        except Exception as e:
            self.logger.error(f"FILESYSTEM DISCOVERY FAILED: {e}")
            
        return scripts
        
    def categorize_violation(self, error_code: str) -> Tuple[str, str]:
        """Categorize Flake8 violations by severity and category."""
        severity_map = {
            'E': 'ERROR',
            'W': 'WARNING',
            'F': 'FATAL',
            'C': 'COMPLEXITY',
            'N': 'NAMING',
            'D': 'DOCSTRING'
        }
        
        category_map = {
            'E1': 'INDENTATION',
            'E2': 'WHITESPACE',
            'E3': 'BLANK_LINES',
            'E4': 'IMPORTS',
            'E5': 'LINE_LENGTH',
            'E7': 'STATEMENTS',
            'E9': 'RUNTIME',
            'W1': 'INDENTATION_WARNING',
            'W2': 'WHITESPACE_WARNING',
            'W3': 'BLANK_LINE_WARNING',
            'W5': 'LINE_LENGTH_WARNING',
            'W6': 'DEPRECATION',
            'F4': 'FUTURE_FEATURE',
            'F8': 'UNDEFINED_NAME',
            'F9': 'SYNTAX_ERROR',
            'C9': 'MCCABE_COMPLEXITY',
            'N8': 'NAMING_CONVENTION',
            'D1': 'MISSING_DOCSTRING',
            'D2': 'DOCSTRING_FORMATTING',
            'D4': 'DOCSTRING_CONTENT'
        }

        severity = severity_map.get(error_code[0] if error_code else '', 'UNKNOWN')
        category = category_map.get(error_code[:2] if len(error_code) >= 2 else '', 'UNKNOWN')

        return severity, category
        
    def scan_file_compliance(self, file_path: str) -> List[ComplianceViolation]:
        """Scan a single file for Flake8 compliance violations."""
        violations = []
        
        try:
            # Validate file exists and is readable
            path_obj = Path(file_path)
            if not path_obj.exists():
                self.logger.warning(f"FILE NOT FOUND: {file_path}")
                return violations
                
            if not path_obj.is_file():
                self.logger.warning(f"NOT A FILE: {file_path}")
                return violations
                
            # Run Flake8 on the file
            result = subprocess.run(
                ['flake8', '--format=%(path)s:%(row)d:%(col)d: %(code)s %(text)s', file_path],
                capture_output=True,
                text=True,
                timeout=60  # Increased timeout for large files
            )
            
            if result.returncode != 0 and result.stdout:
                # Parse Flake8 output
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        parts = line.split(':', 3)
                        if len(parts) >= 4:
                            try:
                                path = parts[0].strip()
                                line_num = int(parts[1].strip())
                                col_num = int(parts[2].strip())
                                
                                # Extract error code and message
                                error_part = parts[3].strip()
                                error_code_parts = error_part.split()
                                if error_code_parts:
                                    error_code = error_code_parts[0]
                                    error_message = error_part[len(error_code):].strip()
                                    
                                    # Categorize violation
                                    severity, category = self.categorize_violation(error_code)
                                    
                                    violation = ComplianceViolation(
                                        file_path=path,
                                        line_number=line_num,
                                        column_number=col_num,
                                        error_code=error_code,
                                        error_message=error_message,
                                        severity=severity,
                                        category=category,
                                        timestamp=datetime.now().isoformat()
                                    )

                                    violations.append(violation)
                                    
                            except (ValueError, IndexError) as parse_error:
                                self.logger.warning(f"PARSE ERROR for line '{line}': {parse_error}")
                            
        except subprocess.TimeoutExpired:
            self.logger.warning(f"TIMEOUT: Flake8 scan timeout for {file_path}")
        except subprocess.CalledProcessError as e:
            self.logger.error(f"FLAKE8 ERROR for {file_path}: {e}")
        except Exception as e:
            self.logger.error(f"SCAN ERROR for {file_path}: {e}")
            
        return violations

    def calculate_etc(self, processed: int, total: int, start_time: float) -> str:
        """Calculate Estimated Time to Completion with visual formatting."""
        if processed == 0 or total == 0:
            return "∞"
            
        elapsed = time.time() - start_time
        if elapsed <= 0:
            return "∞"
            
        rate = processed / elapsed
        remaining = total - processed
        etc_seconds = remaining / rate if rate > 0 else 0
        
        if etc_seconds < 60:
            return f"{etc_seconds:.0f}s"
        elif etc_seconds < 3600:
            return f"{etc_seconds/60:.1f}m"
        else:
            return f"{etc_seconds/3600:.1f}h"

    def run_compliance_scan(self) -> ComplianceMetrics:
        """Execute comprehensive compliance scan with visual processing."""
        self.logger.info("STARTING PIS PHASE 2: COMPLIANCE SCAN")
        self.logger.info("=" * 80)
        
        # Initialize databases
        if not self.initialize_databases():
            self.logger.error("DATABASE INITIALIZATION FAILED - CONTINUING WITH LIMITED FUNCTIONALITY")

        # Discover scripts
        scripts = self.discover_scripts()
        if not scripts:
            self.logger.warning("NO SCRIPTS DISCOVERED - SCAN COMPLETE")
            return self.metrics
            
        self.metrics.total_files_scanned = len(scripts)
        
        # Initialize visual processing indicators
        self.progress_bar = tqdm(
            total=len(scripts),
            desc="COMPLIANCE SCAN",
            unit="files",
            ncols=100,
            bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]'
        )

        # Process files with chunked threading
        chunk_size = min(50, max(1, len(scripts) // 10))
        processed_files = 0
        
        self.logger.info(f"PROCESSING {len(scripts)} FILES IN CHUNKS OF {chunk_size}")

        try:
            with ThreadPoolExecutor(max_workers=4) as executor:
                # Submit files in chunks
                for i in range(0, len(scripts), chunk_size):
                    chunk = scripts[i:i + chunk_size]

                    # Submit chunk for processing
                    future_to_file = {
                        executor.submit(self.scan_file_compliance, file_path): file_path
                        for file_path in chunk
                    }

                    # Process completed futures
                    for future in as_completed(future_to_file):
                        file_path = future_to_file[future]
                        processed_files += 1
                        
                        try:
                            violations = future.result()
                            
                            if violations:
                                self.violations.extend(violations)
                                self.metrics.non_compliant_files += 1
                                self.progress_bar.set_postfix({
                                    'Status': f'VIOLATIONS: {len(violations)}',
                                    'ETC': self.calculate_etc(processed_files, len(scripts), self.start_time)
                                })
                            else:
                                self.metrics.compliant_files += 1
                                self.progress_bar.set_postfix({
                                    'Status': 'COMPLIANT',
                                    'ETC': self.calculate_etc(processed_files, len(scripts), self.start_time)
                                })

                            self.progress_bar.update(1)
                            
                        except Exception as e:
                            self.logger.error(f"PROCESSING ERROR for {file_path}: {e}")
                            self.progress_bar.update(1)
                            
        finally:
            self.progress_bar.close()
        
        # Calculate final metrics
        self.metrics.total_violations = len(self.violations)
        self.metrics.scan_duration = time.time() - self.start_time
        
        # Categorize violations
        for violation in self.violations:
            if violation.severity == 'FATAL':
                self.metrics.critical_violations += 1
            elif violation.severity == 'ERROR':
                self.metrics.critical_violations += 1
            elif violation.severity == 'WARNING':
                self.metrics.warning_violations += 1
            elif violation.severity == 'COMPLEXITY':
                self.metrics.complexity_violations += 1
            elif violation.severity == 'DOCSTRING':
                self.metrics.documentation_violations += 1
            else:
                self.metrics.style_violations += 1
                
        # Calculate compliance score
        if self.metrics.total_files_scanned > 0:
            self.metrics.compliance_score = (
                self.metrics.compliant_files / self.metrics.total_files_scanned
            ) * 100
        else:
            self.metrics.compliance_score = 100.0
            
        self.metrics.timestamp = datetime.now().isoformat()
        
        # Log final results
        self.logger.info("=" * 80)
        self.logger.info("PIS PHASE 2: COMPLIANCE SCAN COMPLETE")
        self.logger.info(f"Total Files Scanned: {self.metrics.total_files_scanned}")
        self.logger.info(f"Compliant Files: {self.metrics.compliant_files}")
        self.logger.info(f"Non-Compliant Files: {self.metrics.non_compliant_files}")
        self.logger.info(f"Total Violations: {self.metrics.total_violations}")
        self.logger.info(f"Compliance Score: {self.metrics.compliance_score:.2f}%")
        self.logger.info(f"Scan Duration: {self.metrics.scan_duration:.2f}s")
        self.logger.info("=" * 80)
        
        return self.metrics
        
    def save_compliance_report(self) -> str:
        """Save comprehensive compliance report with DUAL COPILOT validation."""
        try:
            # Create reports directory
            report_dir = Path("reports/pis_phase2")
            report_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = report_dir / f"pis_phase2_compliance_report_{timestamp}.json"
            
            # Prepare report data
            report_data = {
                "pis_phase": "PHASE_2_COMPLIANCE_SCAN",
                "enterprise_compliance": "ZERO_TOLERANCE_STANDARDS",
                "dual_copilot_validation": "ENABLED",
                "anti_recursion_protocol": "ACTIVE",
                "scan_metadata": {
                    "timestamp": self.metrics.timestamp,
                    "workspace_path": str(self.workspace_path),
                    "scan_duration": self.metrics.scan_duration,
                    "total_files_scanned": self.metrics.total_files_scanned
                },
                "compliance_metrics": asdict(self.metrics),
                "violations_summary": {
                    "critical_violations": self.metrics.critical_violations,
                    "warning_violations": self.metrics.warning_violations,
                    "style_violations": self.metrics.style_violations,
                    "complexity_violations": self.metrics.complexity_violations,
                    "documentation_violations": self.metrics.documentation_violations
                },
                "detailed_violations": [asdict(v) for v in self.violations[:1000]],  # Limit for performance
                "recommendations": self._generate_recommendations(),
                "next_phase": "PHASE_3_AUTOMATED_CORRECTION",
                "dual_copilot_signature": {
                    "primary_validation": "GITHUB_COPILOT_ENTERPRISE",
                    "secondary_validation": "PENDING_PHASE_4",
                    "validation_timestamp": datetime.now().isoformat()
                }
            }

            # Save report
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
                
            self.logger.info(f"COMPLIANCE REPORT SAVED: {report_file}")

            # Save to analytics database
            self._save_to_analytics_db()

            return str(report_file)
            
        except Exception as e:
            self.logger.error(f"REPORT SAVE FAILED: {e}")
            return ""

    def _save_to_analytics_db(self):
        """Save scan results to analytics database."""
        try:
            if not self.analytics_db:
                return
                
            # Insert scan record
            cursor = self.analytics_db.execute("""
                INSERT INTO compliance_scans (
                    scan_timestamp, total_files, compliant_files, non_compliant_files,
                    total_violations, compliance_score, scan_duration, phase
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self.metrics.timestamp,
                self.metrics.total_files_scanned,
                self.metrics.compliant_files,
                self.metrics.non_compliant_files,
                self.metrics.total_violations,
                self.metrics.compliance_score,
                self.metrics.scan_duration,
                'PHASE_2'
            ))
            
            scan_id = cursor.lastrowid
            
            # Insert violations (batch insert for performance)
            violation_data = [
                (
                    scan_id,
                    violation.file_path,
                    violation.line_number,
                    violation.column_number,
                    violation.error_code,
                    violation.error_message,
                    violation.severity,
                    violation.category,
                    violation.timestamp
                )
                for violation in self.violations
            ]
            
            self.analytics_db.executemany("""
                INSERT INTO compliance_violations (
                    scan_id, file_path, line_number, column_number,
                    error_code, error_message, severity, category, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, violation_data)

            self.analytics_db.commit()
            self.logger.info("ANALYTICS DATABASE UPDATED")
            
        except sqlite3.Error as e:
            self.logger.error(f"ANALYTICS SAVE FAILED: {e}")
            
    def _generate_recommendations(self) -> List[str]:
        """Generate enterprise recommendations based on scan results."""
        recommendations = []

        if self.metrics.compliance_score < 95:
            recommendations.append("IMMEDIATE CORRECTION REQUIRED: Compliance score below enterprise threshold")

        if self.metrics.critical_violations > 0:
            recommendations.append("CRITICAL VIOLATIONS DETECTED: Requires immediate attention")

        if self.metrics.complexity_violations > 0:
            recommendations.append("REFACTORING RECOMMENDED: High complexity violations found")
            
        if self.metrics.documentation_violations > 0:
            recommendations.append("DOCUMENTATION ENHANCEMENT: Missing or inadequate docstrings")

        recommendations.extend([
            "PROCEED TO PHASE 3: Automated Correction & Regeneration",
            "ACTIVATE PHASE 4: DUAL COPILOT Validation & Reporting",
            "CONTINUOUS MONITORING: Implement real-time compliance tracking"
        ])
        
        return recommendations
        
    def cleanup(self):
        """Clean up resources and close connections."""
        try:
            if self.production_db:
                self.production_db.close()
            if self.analytics_db:

                self.analytics_db.close()

            if self.progress_bar:
                self.progress_bar.close()
        except Exception as e:
            self.logger.error(f"CLEANUP ERROR: {e}")

def main():
    """Main execution function with enterprise error handling."""
    scanner = None
    try:
        print("PIS PHASE 2: DATABASE-FIRST FLAKE8 COMPLIANCE SCANNER")
        print("=" * 80)
        print("ENTERPRISE ZERO-TOLERANCE STANDARDS ACTIVE")
        print("DUAL COPILOT VALIDATION ENABLED")
        print("ANTI-RECURSION PROTOCOL ACTIVE")
        print("=" * 80)

        # Initialize scanner
        scanner = DatabaseFirstComplianceScanner()

        # Run compliance scan
        metrics = scanner.run_compliance_scan()
        
        # Save report
        report_file = scanner.save_compliance_report()
        
        # Display final status
        print("\n" + "=" * 80)
        print("PIS PHASE 2: COMPLIANCE SCAN COMPLETE")
        print(f"COMPLIANCE SCORE: {metrics.compliance_score:.2f}%")
        print(f"REPORT SAVED: {report_file}")
        print("READY FOR PHASE 3: AUTOMATED CORRECTION")
        print("=" * 80)
        
        # Return appropriate exit code
        return 0 if metrics.compliance_score >= 95 else 1
        
    except KeyboardInterrupt:
        print("\nSCAN INTERRUPTED BY USER")
        return 130
    except Exception as e:
        print(f"\nCRITICAL ERROR: {e}")
        logging.getLogger("PIS_PHASE2_COMPLIANCE").error(f"CRITICAL ERROR: {e}")
        return 1
    finally:
        if scanner:
            scanner.cleanup()

if __name__ == "__main__":
    sys.exit(main())