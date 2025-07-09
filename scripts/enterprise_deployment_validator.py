#!/usr/bin/env python3
"""
Enterprise gh_COPILOT Deployment Validator and Monitor
Advanced validation and monitoring system for enterprise deployment

Features:
- Real-time deployment monitoring
- Comprehensive validation framework
- Performance metrics collection
- Health check system
- Recovery and backup validation
- GitHub Copilot integration testing

Version: 1.0.0
Created: 2025-07-06
"""

import json
import logging
import os
import sqlite3
import subprocess
import sys
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import psutil
import requests

from copilot.common.workspace_utils import get_workspace_path

# Professional logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('deployment_validation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Validation result structure"""
    component: str
    test_name: str
    status: str
    message: str
    duration: float
    timestamp: datetime
    details: Optional[Dict[str, Any]] = None


@dataclass
class PerformanceMetrics:
    """Performance metrics structure"""
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: Dict[str, int]
    process_count: int
    timestamp: datetime


class EnterpriseDeploymentValidator:
    """Comprehensive deployment validation and monitoring system"""

    def __init__(self, deployment_path: Optional[str] = None):
        self.deployment_path = get_workspace_path(deployment_path)
        self.validation_results: List[ValidationResult] = []
        self.performance_metrics: List[PerformanceMetrics] = []
        self.monitoring_active = False
        self.monitoring_thread = None

        # Validation configuration
        self.validation_config = {
            "required_directories": [
                "core",
                "databases",
                "templates",
                "web_gui",
                "scripts",
                "optimization",
                "documentation",
                "deployment",
                "github_integration",
                "backup",
                "monitoring",
                "validation"],
            "required_core_files": [
                "template_intelligence_platform.py",
                "enterprise_performance_monitor_windows.py",
                "enterprise_unicode_compatibility_fix.py",
                "enterprise_json_serialization_fix.py"],
            "required_databases": [
                "production.db",
                "analytics.db",
                "template_completion.db",
                "enhanced_intelligence.db",
                "optimization_metrics.db"],
            "required_documentation": [
                "README.md",
                "INSTALLATION_GUIDE.md",
                "SYSTEM_OVERVIEW.md",
                "DEPLOYMENT_REPORT.md"],
            "required_scripts": [
                "install.py",
                "start.py",
                "install.bat"],
            "performance_thresholds": {
                "cpu_usage_max": 80.0,
                "memory_usage_max": 80.0,
                "disk_usage_max": 90.0,
                "response_time_max": 5.0}}

        # Initialize validation database
        self.init_validation_database()

    def init_validation_database(self):
        """Initialize validation tracking database"""
        try:
            db_path = self.deployment_path / "validation" / "validation_tracking.db"
            db_path.parent.mkdir(parents=True, exist_ok=True)

            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Create validation results table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS validation_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    component TEXT NOT NULL,
                    test_name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    message TEXT,
                    duration REAL,
                    timestamp TEXT,
                    details TEXT
                )
            """)

            # Create performance metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cpu_usage REAL,
                    memory_usage REAL,
                    disk_usage REAL,
                    network_io TEXT,
                    process_count INTEGER,
                    timestamp TEXT
                )
            """)

            # Create deployment status table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS deployment_status (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    component TEXT NOT NULL,
                    status TEXT NOT NULL,
                    last_check TEXT,
                    health_score REAL,
                    error_count INTEGER DEFAULT 0
                )
            """)

            conn.commit()
            conn.close()

            logger.info("✅ Validation database initialized")

        except Exception as e:
            logger.error(f"❌ Error initializing validation database: {e}")

    def validate_directory_structure(self) -> List[ValidationResult]:
        """Validate complete directory structure"""
        results = []

        for directory in self.validation_config["required_directories"]:
            start_time = time.time()
            dir_path = self.deployment_path / directory

            if dir_path.exists() and dir_path.is_dir():
                result = ValidationResult(
                    component="directory_structure",
                    test_name=f"check_directory_{directory}",
                    status="PASSED",
                    message=f"Directory {directory} exists",
                    duration=time.time() - start_time,
                    timestamp=datetime.now()
                )
            else:
                result = ValidationResult(
                    component="directory_structure",
                    test_name=f"check_directory_{directory}",
                    status="FAILED",
                    message=f"Directory {directory} missing",
                    duration=time.time() - start_time,
                    timestamp=datetime.now()
                )

            results.append(result)

        return results

    def validate_core_systems(self) -> List[ValidationResult]:
        """Validate core system files"""
        results = []
        core_dir = self.deployment_path / "core"

        for core_file in self.validation_config["required_core_files"]:
            start_time = time.time()
            file_path = core_dir / core_file

            if file_path.exists() and file_path.is_file():
                # Check file size
                file_size = file_path.stat().st_size
                if file_size > 0:
                    result = ValidationResult(
                        component="core_systems",
                        test_name=f"check_core_file_{core_file}",
                        status="PASSED",
                        message=f"Core file {core_file} exists ({file_size} bytes)",
                        duration=time.time() - start_time,
                        timestamp=datetime.now(),
                        details={
                            "file_size": file_size})
                else:
                    result = ValidationResult(
                        component="core_systems",
                        test_name=f"check_core_file_{core_file}",
                        status="FAILED",
                        message=f"Core file {core_file} is empty",
                        duration=time.time() - start_time,
                        timestamp=datetime.now()
                    )
            else:
                result = ValidationResult(
                    component="core_systems",
                    test_name=f"check_core_file_{core_file}",
                    status="FAILED",
                    message=f"Core file {core_file} missing",
                    duration=time.time() - start_time,
                    timestamp=datetime.now()
                )

            results.append(result)

        return results

    def validate_databases(self) -> List[ValidationResult]:
        """Validate database files and connections"""
        results = []
        db_dir = self.deployment_path / "databases"

        for db_file in self.validation_config["required_databases"]:
            start_time = time.time()
            db_path = db_dir / db_file

            if db_path.exists() and db_path.is_file():
                # Test database connection
                try:
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    cursor.execute(
                        "SELECT name FROM sqlite_master WHERE type='table';")
                    tables = cursor.fetchall()
                    conn.close()

                    result = ValidationResult(
                        component="databases",
                        test_name=f"check_database_{db_file}",
                        status="PASSED",
                        message=f"Database {db_file} accessible ({len(tables)} tables)",
                        duration=time.time() - start_time,
                        timestamp=datetime.now(),
                        details={"table_count": len(tables)}
                    )
                except Exception as e:
                    result = ValidationResult(
                        component="databases",
                        test_name=f"check_database_{db_file}",
                        status="FAILED",
                        message=f"Database {db_file} connection failed: {e}",
                        duration=time.time() - start_time,
                        timestamp=datetime.now()
                    )
            else:
                result = ValidationResult(
                    component="databases",
                    test_name=f"check_database_{db_file}",
                    status="FAILED",
                    message=f"Database {db_file} missing",
                    duration=time.time() - start_time,
                    timestamp=datetime.now()
                )

            results.append(result)

        return results

    def validate_template_intelligence_platform(
            self) -> List[ValidationResult]:
        """Validate Template Intelligence Platform"""
        results = []

        # Check template intelligence platform file
        start_time = time.time()
        platform_file = self.deployment_path / \
            "core" / "template_intelligence_platform.py"

        if platform_file.exists():
            try:
                # Test import
                import importlib.util
                spec = importlib.util.spec_from_file_location(
                    "template_intelligence_platform", platform_file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                result = ValidationResult(
                    component="template_intelligence",
                    test_name="platform_import_test",
                    status="PASSED",
                    message="Template Intelligence Platform imports successfully",
                    duration=time.time() - start_time,
                    timestamp=datetime.now())
            except Exception as e:
                result = ValidationResult(
                    component="template_intelligence",
                    test_name="platform_import_test",
                    status="FAILED",
                    message=f"Template Intelligence Platform import failed: {e}",
                    duration=time.time() - start_time,
                    timestamp=datetime.now())
        else:
            result = ValidationResult(
                component="template_intelligence",
                test_name="platform_import_test",
                status="FAILED",
                message="Template Intelligence Platform file missing",
                duration=time.time() - start_time,
                timestamp=datetime.now()
            )

        results.append(result)

        # Check templates directory
        start_time = time.time()
        templates_dir = self.deployment_path / "templates"

        if templates_dir.exists():
            template_count = len(list(templates_dir.glob("**/*.py")))
            result = ValidationResult(
                component="template_intelligence",
                test_name="templates_directory_check",
                status="PASSED",
                message=f"Templates directory exists ({template_count} template files)",
                duration=time.time() - start_time,
                timestamp=datetime.now(),
                details={
                    "template_count": template_count})
        else:
            result = ValidationResult(
                component="template_intelligence",
                test_name="templates_directory_check",
                status="FAILED",
                message="Templates directory missing",
                duration=time.time() - start_time,
                timestamp=datetime.now()
            )

        results.append(result)

        return results

    def validate_web_gui(self) -> List[ValidationResult]:
        """Validate web GUI deployment"""
        results = []

        # Check web GUI directory
        start_time = time.time()
        web_gui_dir = self.deployment_path / "web_gui"

        if web_gui_dir.exists():
            gui_files = list(web_gui_dir.glob("**/*.py"))
            result = ValidationResult(
                component="web_gui",
                test_name="web_gui_files_check",
                status="PASSED",
                message=f"Web GUI directory exists ({len(gui_files)} Python files)",
                duration=time.time() - start_time,
                timestamp=datetime.now(),
                details={"gui_file_count": len(gui_files)}
            )
        else:
            result = ValidationResult(
                component="web_gui",
                test_name="web_gui_files_check",
                status="FAILED",
                message="Web GUI directory missing",
                duration=time.time() - start_time,
                timestamp=datetime.now()
            )

        results.append(result)

        return results

    def validate_github_integration(self) -> List[ValidationResult]:
        """Validate GitHub Copilot integration"""
        results = []

        # Check GitHub integration directory
        start_time = time.time()
        github_dir = self.deployment_path / "github_integration"

        if github_dir.exists():
            instruction_files = list(github_dir.glob("*.md"))
            result = ValidationResult(
                component="github_integration",
                test_name="github_integration_check",
                status="PASSED",
                message=f"GitHub integration directory exists ({
                    len(instruction_files)} instruction files)",
                duration=time.time() - start_time,
                timestamp=datetime.now(),
                details={
                    "instruction_file_count": len(instruction_files)})
        else:
            result = ValidationResult(
                component="github_integration",
                test_name="github_integration_check",
                status="FAILED",
                message="GitHub integration directory missing",
                duration=time.time() - start_time,
                timestamp=datetime.now()
            )

        results.append(result)

        return results

    def validate_installation_scripts(self) -> List[ValidationResult]:
        """Validate installation scripts"""
        results = []
        deployment_dir = self.deployment_path / "deployment"

        for script in self.validation_config["required_scripts"]:
            start_time = time.time()
            script_path = deployment_dir / script

            if script_path.exists() and script_path.is_file():
                # Check script permissions and content
                script_size = script_path.stat().st_size
                if script_size > 0:
                    result = ValidationResult(
                        component="installation_scripts",
                        test_name=f"check_script_{script}",
                        status="PASSED",
                        message=f"Installation script {script} exists ({script_size} bytes)",
                        duration=time.time() - start_time,
                        timestamp=datetime.now(),
                        details={
                            "script_size": script_size})
                else:
                    result = ValidationResult(
                        component="installation_scripts",
                        test_name=f"check_script_{script}",
                        status="FAILED",
                        message=f"Installation script {script} is empty",
                        duration=time.time() - start_time,
                        timestamp=datetime.now()
                    )
            else:
                result = ValidationResult(
                    component="installation_scripts",
                    test_name=f"check_script_{script}",
                    status="FAILED",
                    message=f"Installation script {script} missing",
                    duration=time.time() - start_time,
                    timestamp=datetime.now()
                )

            results.append(result)

        return results

    def validate_documentation(self) -> List[ValidationResult]:
        """Validate documentation completeness"""
        results = []
        docs_dir = self.deployment_path / "documentation"

        for doc in self.validation_config["required_documentation"]:
            start_time = time.time()
            doc_path = docs_dir / doc

            if doc_path.exists() and doc_path.is_file():
                doc_size = doc_path.stat().st_size
                if doc_size > 0:
                    result = ValidationResult(
                        component="documentation",
                        test_name=f"check_documentation_{doc}",
                        status="PASSED",
                        message=f"Documentation {doc} exists ({doc_size} bytes)",
                        duration=time.time() - start_time,
                        timestamp=datetime.now(),
                        details={
                            "doc_size": doc_size})
                else:
                    result = ValidationResult(
                        component="documentation",
                        test_name=f"check_documentation_{doc}",
                        status="FAILED",
                        message=f"Documentation {doc} is empty",
                        duration=time.time() - start_time,
                        timestamp=datetime.now()
                    )
            else:
                result = ValidationResult(
                    component="documentation",
                    test_name=f"check_documentation_{doc}",
                    status="FAILED",
                    message=f"Documentation {doc} missing",
                    duration=time.time() - start_time,
                    timestamp=datetime.now()
                )

            results.append(result)

        return results

    def collect_performance_metrics(self) -> PerformanceMetrics:
        """Collect system performance metrics"""
        try:
            # Get system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            network = psutil.net_io_counters()

            metrics = PerformanceMetrics(
                cpu_usage=cpu_percent,
                memory_usage=memory.percent,
                disk_usage=disk.percent,
                network_io={
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv,
                    "packets_sent": network.packets_sent,
                    "packets_recv": network.packets_recv
                },
                process_count=len(psutil.pids()),
                timestamp=datetime.now()
            )

            return metrics

        except Exception as e:
            logger.error(f"❌ Error collecting performance metrics: {e}")
            return None

    def start_performance_monitoring(self, interval: int = 60):
        """Start continuous performance monitoring"""
        def monitor():
            while self.monitoring_active:
                try:
                    metrics = self.collect_performance_metrics()
                    if metrics:
                        self.performance_metrics.append(metrics)
                        self.store_performance_metrics(metrics)

                        # Check thresholds
                        self.check_performance_thresholds(metrics)

                    time.sleep(interval)
                except Exception as e:
                    logger.error(f"❌ Error in performance monitoring: {e}")
                    time.sleep(interval)

        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=monitor)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()

        logger.info("📊 Performance monitoring started")

    def stop_performance_monitoring(self):
        """Stop performance monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join()
        logger.info("📊 Performance monitoring stopped")

    def check_performance_thresholds(self, metrics: PerformanceMetrics):
        """Check performance thresholds and alert if exceeded"""
        thresholds = self.validation_config["performance_thresholds"]

        alerts = []

        if metrics.cpu_usage > thresholds["cpu_usage_max"]:
            alerts.append(f"⚠️ High CPU usage: {metrics.cpu_usage:.1f}%")

        if metrics.memory_usage > thresholds["memory_usage_max"]:
            alerts.append(f"⚠️ High memory usage: {metrics.memory_usage:.1f}%")

        if metrics.disk_usage > thresholds["disk_usage_max"]:
            alerts.append(f"⚠️ High disk usage: {metrics.disk_usage:.1f}%")

        if alerts:
            for alert in alerts:
                logger.warning(alert)

            # Store alerts
            self.store_performance_alerts(alerts, metrics.timestamp)

    def store_validation_results(self, results: List[ValidationResult]):
        """Store validation results in database"""
        try:
            db_path = self.deployment_path / "validation" / "validation_tracking.db"
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            for result in results:
                cursor.execute("""
                    INSERT INTO validation_results
                    (component, test_name, status, message, duration, timestamp, details)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    result.component,
                    result.test_name,
                    result.status,
                    result.message,
                    result.duration,
                    result.timestamp.isoformat(),
                    json.dumps(result.details) if result.details else None
                ))

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"❌ Error storing validation results: {e}")

    def store_performance_metrics(self, metrics: PerformanceMetrics):
        """Store performance metrics in database"""
        try:
            db_path = self.deployment_path / "validation" / "validation_tracking.db"
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO performance_metrics
                (cpu_usage, memory_usage, disk_usage, network_io, process_count, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                metrics.cpu_usage,
                metrics.memory_usage,
                metrics.disk_usage,
                json.dumps(metrics.network_io),
                metrics.process_count,
                metrics.timestamp.isoformat()
            ))

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"❌ Error storing performance metrics: {e}")

    def store_performance_alerts(self, alerts: List[str], timestamp: datetime):
        """Store performance alerts"""
        try:
            alerts_file = self.deployment_path / "monitoring" / "performance_alerts.json"
            alerts_file.parent.mkdir(parents=True, exist_ok=True)

            alert_data = {
                "timestamp": timestamp.isoformat(),
                "alerts": alerts
            }

            # Read existing alerts
            existing_alerts = []
            if alerts_file.exists():
                try:
                    with open(alerts_file, 'r') as f:
                        existing_alerts = json.load(f)
                except BaseException:
                    existing_alerts = []

            # Add new alert
            existing_alerts.append(alert_data)

            # Keep only last 100 alerts
            if len(existing_alerts) > 100:
                existing_alerts = existing_alerts[-100:]

            # Save alerts
            with open(alerts_file, 'w') as f:
                json.dump(existing_alerts, f, indent=2)

        except Exception as e:
            logger.error(f"❌ Error storing performance alerts: {e}")

    def run_comprehensive_validation(self) -> Dict[str, Any]:
        """Run comprehensive validation of entire deployment"""
        logger.info("🔍 Starting comprehensive deployment validation...")

        all_results = []

        # Run all validation tests
        validation_tests = [
            ("Directory Structure", self.validate_directory_structure),
            ("Core Systems", self.validate_core_systems),
            ("Databases", self.validate_databases),
            ("Template Intelligence", self.validate_template_intelligence_platform),
            ("Web GUI", self.validate_web_gui),
            ("GitHub Integration", self.validate_github_integration),
            ("Installation Scripts", self.validate_installation_scripts),
            ("Documentation", self.validate_documentation)
        ]

        for test_name, test_func in validation_tests:
            logger.info(f"🔄 Running {test_name} validation...")
            results = test_func()
            all_results.extend(results)

            # Store results
            self.store_validation_results(results)

            # Log summary
            passed = sum(1 for r in results if r.status == "PASSED")
            failed = sum(1 for r in results if r.status == "FAILED")
            logger.info(f"✅ {test_name}: {passed} passed, {failed} failed")

        # Calculate overall statistics
        total_tests = len(all_results)
        passed_tests = sum(1 for r in all_results if r.status == "PASSED")
        failed_tests = sum(1 for r in all_results if r.status == "FAILED")
        success_rate = (passed_tests / total_tests) * \
            100 if total_tests > 0 else 0

        validation_summary = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate,
            "validation_timestamp": datetime.now().isoformat(),
            "results": all_results
        }

        # Save validation summary
        self.save_validation_summary(validation_summary)

        logger.info(
            f"🎯 Validation complete: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}%)")

        return validation_summary

    def save_validation_summary(self, summary: Dict[str, Any]):
        """Save validation summary to file"""
        try:
            summary_file = self.deployment_path / "validation" / "validation_summary.json"
            summary_file.parent.mkdir(parents=True, exist_ok=True)

            # Convert ValidationResult objects to dictionaries for JSON
            # serialization
            json_results = []
            for result in summary["results"]:
                json_results.append({
                    "component": result.component,
                    "test_name": result.test_name,
                    "status": result.status,
                    "message": result.message,
                    "duration": result.duration,
                    "timestamp": result.timestamp.isoformat(),
                    "details": result.details
                })

            summary["results"] = json_results

            with open(summary_file, 'w') as f:
                json.dump(summary, f, indent=2)

            # Generate markdown report
            self.generate_validation_report(summary)

        except Exception as e:
            logger.error(f"❌ Error saving validation summary: {e}")

    def generate_validation_report(self, summary: Dict[str, Any]):
        """Generate validation report in markdown format"""
        try:
            report_file = self.deployment_path / "validation" / "VALIDATION_REPORT.md"

            report = f"""# gh_COPILOT Deployment Validation Report

## Summary

- **Total Tests**: {summary['total_tests']}
- **Passed Tests**: {summary['passed_tests']}
- **Failed Tests**: {summary['failed_tests']}
- **Success Rate**: {summary['success_rate']:.1f}%
- **Validation Date**: {summary['validation_timestamp']}

## Test Results by Component

"""

            # Group results by component
            components = {}
            for result in summary["results"]:
                component = result["component"]
                if component not in components:
                    components[component] = []
                components[component].append(result)

            for component, results in components.items():
                passed = sum(1 for r in results if r["status"] == "PASSED")
                failed = sum(1 for r in results if r["status"] == "FAILED")

                report += f"### {component.replace('_', ' ').title()}\n\n"
                report += f"- **Status**: {passed} passed, {failed} failed\n"
                report += f"- **Tests**:\n"

                for result in results:
                    status_icon = "✅" if result["status"] == "PASSED" else "❌"
                    report += f"  - {status_icon} {
                        result['test_name']}: {
                        result['message']}\n"

                report += "\n"

            # Add performance metrics section if available
            if self.performance_metrics:
                latest_metrics = self.performance_metrics[-1]
                report += f"""## Performance Metrics

- **CPU Usage**: {latest_metrics.cpu_usage:.1f}%
- **Memory Usage**: {latest_metrics.memory_usage:.1f}%
- **Disk Usage**: {latest_metrics.disk_usage:.1f}%
- **Process Count**: {latest_metrics.process_count}
- **Last Updated**: {latest_metrics.timestamp.isoformat()}

"""

            report += """## Recommendations

"""

            if summary["failed_tests"] > 0:
                report += "### Failed Tests\n\n"
                for result in summary["results"]:
                    if result["status"] == "FAILED":
                        report += f"- **{result['component']}**: {result['message']}\n"
                report += "\n"

            if summary["success_rate"] < 100:
                report += "### Action Items\n\n"
                report += "1. Review and resolve failed tests\n"
                report += "2. Re-run validation after fixes\n"
                report += "3. Check logs for detailed error information\n"
                report += "4. Verify all dependencies are installed\n\n"

            report += """## Next Steps

1. **If all tests passed**: Run `python deployment/start.py` to start the system
2. **If tests failed**: Address the issues and re-run validation
3. **For ongoing monitoring**: Use `python validation/monitor.py` for continuous monitoring

## Support

For technical support, see:
- `documentation/troubleshooting_guide.md`
- `documentation/INSTALLATION_GUIDE.md`
- Validation logs in `validation/validation_tracking.db`
"""

            with open(report_file, 'w') as f:
                f.write(report)

            logger.info(f"📄 Validation report generated: {report_file}")

        except Exception as e:
            logger.error(f"❌ Error generating validation report: {e}")

    def health_check(self) -> Dict[str, Any]:
        """Perform quick health check"""
        logger.info("🏥 Performing health check...")

        health_status = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "HEALTHY",
            "components": {}
        }

        # Check critical components
        critical_checks = [
            ("deployment_directory", lambda: self.deployment_path.exists()),
            ("core_directory", lambda: (self.deployment_path / "core").exists()),
            ("databases_directory", lambda: (self.deployment_path / "databases").exists()),
            ("documentation_directory", lambda: (self.deployment_path / "documentation").exists())
        ]

        for check_name, check_func in critical_checks:
            try:
                result = check_func()
                health_status["components"][check_name] = {
                    "status": "HEALTHY" if result else "UNHEALTHY",
                    "message": "OK" if result else "Component missing or inaccessible"}
            except Exception as e:
                health_status["components"][check_name] = {
                    "status": "ERROR",
                    "message": str(e)
                }

        # Check system resources
        try:
            metrics = self.collect_performance_metrics()
            if metrics:
                thresholds = self.validation_config["performance_thresholds"]

                health_status["components"]["system_resources"] = {
                    "status": "HEALTHY",
                    "cpu_usage": metrics.cpu_usage,
                    "memory_usage": metrics.memory_usage,
                    "disk_usage": metrics.disk_usage,
                    "warnings": []
                }

                if metrics.cpu_usage > thresholds["cpu_usage_max"]:
                    health_status["components"]["system_resources"]["warnings"].append(
                        "High CPU usage")

                if metrics.memory_usage > thresholds["memory_usage_max"]:
                    health_status["components"]["system_resources"]["warnings"].append(
                        "High memory usage")

                if metrics.disk_usage > thresholds["disk_usage_max"]:
                    health_status["components"]["system_resources"]["warnings"].append(
                        "High disk usage")

                if health_status["components"]["system_resources"]["warnings"]:
                    health_status["components"]["system_resources"]["status"] = "WARNING"

        except Exception as e:
            health_status["components"]["system_resources"] = {
                "status": "ERROR",
                "message": str(e)
            }

        # Determine overall status
        component_statuses = [comp["status"]
                              for comp in health_status["components"].values()]
        if "ERROR" in component_statuses:
            health_status["overall_status"] = "ERROR"
        elif "UNHEALTHY" in component_statuses:
            health_status["overall_status"] = "UNHEALTHY"
        elif "WARNING" in component_statuses:
            health_status["overall_status"] = "WARNING"

        # Save health check results
        health_file = self.deployment_path / "monitoring" / "health_check.json"
        health_file.parent.mkdir(parents=True, exist_ok=True)

        with open(health_file, 'w') as f:
            json.dump(health_status, f, indent=2)

        logger.info(
            f"🏥 Health check complete: {
                health_status['overall_status']}")

        return health_status


def main():
    """Main execution function"""
    import argparse

    parser = argparse.ArgumentParser(
        description='gh_COPILOT Enterprise Deployment Validator')
    parser.add_argument(
        '--path',
        default=os.getenv(
            'GH_COPILOT_WORKSPACE',
            '/path/to/workspace'),
        help='Deployment path')
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Run comprehensive validation')
    parser.add_argument(
        '--monitor',
        action='store_true',
        help='Start performance monitoring')
    parser.add_argument(
        '--health',
        action='store_true',
        help='Run health check')
    parser.add_argument('--interval', type=int, default=60,
                        help='Monitoring interval (seconds)')

    args = parser.parse_args()

    # Initialize validator
    validator = EnterpriseDeploymentValidator(args.path)

    if args.validate:
        # Run comprehensive validation
        validator.run_comprehensive_validation()
    elif args.monitor:
        # Start monitoring
        validator.start_performance_monitoring(args.interval)
        try:
            while True:
                time.sleep(10)
        except KeyboardInterrupt:
            validator.stop_performance_monitoring()
    elif args.health:
        # Run health check
        validator.health_check()
    else:
        # Run quick validation by default
        validator.run_comprehensive_validation()


if __name__ == "__main__":
    main()
