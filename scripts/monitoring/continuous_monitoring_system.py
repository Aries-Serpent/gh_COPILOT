#!/usr/bin/env python3
"""
"stats" CONTINUOUS MONITORING SYSTEM
Enterprise-grade continuous monitoring for 12,635+ violations
Real-time tracking, alerting, and automated correction monitoring
"""

import json
import logging
import os
import sqlite3
import sys
import threading
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Tuple

from unified_monitoring_optimization_system import (
    _update_dashboard,
    push_metrics,
)

from tqdm import tqdm

# MANDATORY: Anti-recursion validation


def validate_workspace_integrity() -> bool:
    """CRITICAL: Validate workspace integrity before operations."""
    workspace_root = Path(os.getcwd())

    # Check for recursive patterns
    forbidden_patterns = ["*backup*", "*_backup_*", "backups", "*temp*"]
    violations = []

    for pattern in forbidden_patterns:
        for folder in workspace_root.rglob(pattern):
            if folder.is_dir() and folder != workspace_root:
                violations.append(str(folder))

    if violations:
        for violation in violations:
            print(f"# ALERT RECURSIVE VIOLATION: {violation}")
        raise RuntimeError("CRITICAL: Recursive violations prevent execution")

    return True


@dataclass
class MonitoringSnapshot:
    """stats" Monitoring data snapshot"""

    timestamp: datetime
    total_violations: int
    pending_violations: int
    fixed_violations: int
    new_violations: int
    files_with_violations: int
    top_violation_types: List[Tuple[str, int]]
    critical_violations: int
    health_score: float


@dataclass
class AlertThreshold:
    """# ALERT Alert threshold configuration"""

    metric: str
    threshold_value: float
    comparison: str  # 'greater_than', 'less_than', 'equals'
    severity: str  # 'INFO', 'WARNING', 'CRITICAL'
    enabled: bool


class ContinuousMonitoringSystem:
    """stats" Enterprise-grade continuous monitoring system"""

    def __init__(self, workspace_path: str = "e:/gh_COPILOT"):
        # CRITICAL: Validate workspace integrity
        validate_workspace_integrity()

        self.workspace_path = Path(workspace_path)
        self.database_path = self.workspace_path / "databases" / "flake8_violations.db"
        self.monitoring_dir = self.workspace_path / "monitoring"
        self.monitoring_dir.mkdir(exist_ok=True)

        # Monitoring configuration
        self.monitoring_interval = 300  # 5 minutes
        self.snapshot_retention_days = 30
        self.is_monitoring = False
        self.monitoring_thread = None

        # Initialize components
        self.setup_logging()
        self.setup_monitoring_database()
        self.setup_alert_thresholds()

        print("📊 CONTINUOUS MONITORING SYSTEM INITIALIZED")
        print(f"Database: {self.database_path}")
        print(f"Monitoring: {self.monitoring_dir}")
        print(f"Interval: {self.monitoring_interval} seconds")

    def setup_logging(self):
        """📋 Setup enterprise logging"""
        log_dir = self.workspace_path / "logs"
        log_dir.mkdir(exist_ok=True)

        # Create file handler with UTF-8 encoding
        file_handler = logging.FileHandler(log_dir / "continuous_monitoring.log", encoding="utf-8")
        file_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))

        # Setup logger
        self.logger = logging.getLogger("continuous_monitoring")
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(file_handler)

    def setup_monitoring_database(self):
        """🗄️ Setup monitoring database tables"""
        monitoring_db = self.monitoring_dir / "monitoring.db"

        with sqlite3.connect(monitoring_db) as conn:
            cursor = conn.cursor()

            # Create monitoring snapshots table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS monitoring_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    total_violations INTEGER,
                    pending_violations INTEGER,
                    fixed_violations INTEGER,
                    new_violations INTEGER,
                    files_with_violations INTEGER,
                    critical_violations INTEGER,
                    health_score REAL,
                    snapshot_data TEXT
                )
            """)

            # Create alerts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    alert_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    metric TEXT NOT NULL,
                    current_value REAL,
                    threshold_value REAL,
                    message TEXT,
                    acknowledged BOOLEAN DEFAULT FALSE
                )
            """)

            # Create metrics history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS metrics_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    metric_value REAL,
                    metadata TEXT
                )
            """)

        self.monitoring_db = monitoring_db

    def setup_alert_thresholds(self):
        """# ALERT Setup alert thresholds"""
        self.alert_thresholds = [
            AlertThreshold("new_violations", 100, "greater_than", "WARNING", True),
            AlertThreshold("critical_violations", 10, "greater_than", "CRITICAL", True),
            AlertThreshold("health_score", 70.0, "less_than", "WARNING", True),
            AlertThreshold("health_score", 50.0, "less_than", "CRITICAL", True),
            AlertThreshold("pending_violations", 15000, "greater_than", "WARNING", True),
            AlertThreshold("files_with_violations", 1000, "greater_than", "INFO", True),
        ]

    def collect_monitoring_snapshot(self) -> MonitoringSnapshot:
        """stats" Collect current monitoring snapshot"""
        with sqlite3.connect(self.database_path) as conn:
            cursor = conn.cursor()

            # Total violations
            cursor.execute("SELECT COUNT(*) FROM violations")
            total_violations = cursor.fetchone()[0]

            # Pending violations
            cursor.execute("SELECT COUNT(*) FROM violations WHERE status = 'pending'")
            pending_violations = cursor.fetchone()[0]

            # Fixed violations
            cursor.execute("SELECT COUNT(*) FROM violations WHERE status = 'fixed'")
            fixed_violations = cursor.fetchone()[0]

            # New violations (using session-based approach since no created_at column)
            cursor.execute("""
                SELECT COUNT(*) FROM violations
                WHERE status = 'pending'
            """)
            result = cursor.fetchone()
            total_pending = result[0] if result else 0
            # Use a subset as "new" violations since we don't have timestamps'
            new_violations = min(100, total_pending)

            # Files with violations
            cursor.execute("""
                SELECT COUNT(DISTINCT file_path) FROM violations
                WHERE status = 'pending'
            """)
            files_with_violations = cursor.fetchone()[0]

            # Top violation types
            cursor.execute("""
                SELECT error_code, COUNT(*) as count
                FROM violations
                WHERE status = 'pending'
                GROUP BY error_code
                ORDER BY COUNT(*) DESC
                LIMIT 5
            """)
            top_violation_types = cursor.fetchall()

            # Critical violations (assuming F8xx series are critical)
            cursor.execute("""
                SELECT COUNT(*) FROM violations
                WHERE status = 'pending' AND error_code LIKE 'F8%'
            """)
            critical_violations = cursor.fetchone()[0]

            # Calculate health score (0-100)
            health_score = max(0, 100 - (pending_violations / 100))  # Simple metric

            return MonitoringSnapshot(
                timestamp=datetime.now(),
                total_violations=total_violations,
                pending_violations=pending_violations,
                fixed_violations=fixed_violations,
                new_violations=new_violations,
                files_with_violations=files_with_violations,
                top_violation_types=top_violation_types,
                critical_violations=critical_violations,
                health_score=health_score,
            )

    def save_snapshot(self, snapshot: MonitoringSnapshot):
        """# # 💾 Save monitoring snapshot to database"""
        with sqlite3.connect(self.monitoring_db) as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO monitoring_snapshots
                (timestamp, total_violations, pending_violations, fixed_violations,
                 new_violations, files_with_violations, critical_violations,
                 health_score, snapshot_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    snapshot.timestamp.isoformat(),
                    snapshot.total_violations,
                    snapshot.pending_violations,
                    snapshot.fixed_violations,
                    snapshot.new_violations,
                    snapshot.files_with_violations,
                    snapshot.critical_violations,
                    snapshot.health_score,
                    json.dumps(asdict(snapshot), default=str),
                ),
            )

    def check_alert_thresholds(self, snapshot: MonitoringSnapshot) -> List[Dict[str, Any]]:
        """# ALERT Check if any alert thresholds are exceeded"""
        alerts = []

        snapshot_values = {
            "new_violations": snapshot.new_violations,
            "critical_violations": snapshot.critical_violations,
            "health_score": snapshot.health_score,
            "pending_violations": snapshot.pending_violations,
            "files_with_violations": snapshot.files_with_violations,
            "total_violations": snapshot.total_violations,
        }

        for threshold in self.alert_thresholds:
            if not threshold.enabled:
                continue

            current_value = snapshot_values.get(threshold.metric, 0)
            triggered = False

            if threshold.comparison == "greater_than" and current_value > threshold.threshold_value:
                triggered = True
            elif threshold.comparison == "less_than" and current_value < threshold.threshold_value:
                triggered = True
            elif threshold.comparison == "equals" and current_value == threshold.threshold_value:
                triggered = True

            if triggered:
                alert = {
                    "timestamp": snapshot.timestamp.isoformat(),
                    "alert_type": f"THRESHOLD_EXCEEDED_{threshold.metric.upper()}",
                    "severity": threshold.severity,
                    "metric": threshold.metric,
                    "current_value": current_value,
                    "threshold_value": threshold.threshold_value,
                    "message": f"{threshold.metric} is {current_value}, threshold is {threshold.threshold_value}",
                    "acknowledged": False,
                }
                alerts.append(alert)

        return alerts

    def save_alerts(self, alerts: List[Dict[str, Any]]):
        """# ALERT Save alerts to database"""
        if not alerts:
            return

        with sqlite3.connect(self.monitoring_db) as conn:
            cursor = conn.cursor()

            for alert in alerts:
                cursor.execute(
                    """
                    INSERT INTO alerts
                    (timestamp, alert_type, severity, metric, current_value,
                     threshold_value, message, acknowledged)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        alert["timestamp"],
                        alert["alert_type"],
                        alert["severity"],
                        alert["metric"],
                        alert["current_value"],
                        alert["threshold_value"],
                        alert["message"],
                        alert["acknowledged"],
                    ),
                )

    def monitor_cycle(self):
        """stats" Single monitoring cycle"""
        try:
            # Collect snapshot
            snapshot = self.collect_monitoring_snapshot()

            # Save snapshot
            self.save_snapshot(snapshot)

            # Check alerts
            alerts = self.check_alert_thresholds(snapshot)

            # Save alerts
            if alerts:
                self.save_alerts(alerts)
                self.logger.warning(f"Generated {len(alerts)} alerts")
                for alert in alerts:
                    print(f"# ALERT {alert['severity']}: {alert['message']}")

            # Log status
            self.logger.info(
                f"Monitoring cycle: {snapshot.pending_violations:,} pending, {snapshot.health_score:.1f}% health"
            )

            return snapshot, alerts

        except Exception as e:
            self.logger.error(f"Error in monitoring cycle: {e}")
            return None, []

    def continuous_monitoring_loop(self):
        """# # # 🔄 Continuous monitoring loop"""
        print(f"📊 Starting continuous monitoring (interval: {self.monitoring_interval}s)")

        while self.is_monitoring:
            start_time = time.time()

            snapshot, alerts = self.monitor_cycle()

            if snapshot:
                # Print status update
                print(
                    f"[{datetime.now().strftime('%H:%M:%S')}] "
                    f"Pending: {snapshot.pending_violations:,} | "
                    f"Health: {snapshot.health_score:.1f}% | "
                    f"Alerts: {len(alerts)}"
                )

            # Sleep for remaining interval time
            elapsed = time.time() - start_time
            sleep_time = max(0, self.monitoring_interval - elapsed)

            # Sleep in small chunks to allow for clean shutdown
            while sleep_time > 0 and self.is_monitoring:
                chunk_sleep = min(1.0, sleep_time)
                time.sleep(chunk_sleep)
                sleep_time -= chunk_sleep

    def start_monitoring(self):
        """rocket" Start continuous monitoring"""
        if self.is_monitoring:
            print("# # WARNING  Monitoring already running")
            return

        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(target=self.continuous_monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        print("# # SUCCESS Continuous monitoring started")

    def stop_monitoring(self):
        """🛑 Stop continuous monitoring"""
        if not self.is_monitoring:
            print("# # WARNING  Monitoring not running")
            return

        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        print("# # SUCCESS Continuous monitoring stopped")

    def get_monitoring_dashboard(self) -> Dict[str, Any]:
        """📋 Get monitoring dashboard data"""
        current_snapshot = self.collect_monitoring_snapshot()

        # Get recent alerts
        with sqlite3.connect(self.monitoring_db) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT alert_type, severity, message, timestamp
                FROM alerts
                WHERE timestamp > datetime('now', '-24 hours')
                ORDER BY timestamp DESC
                LIMIT 10
            """)
            recent_alerts = cursor.fetchall()

            # Get trends (last 24 hours)
            cursor.execute("""
                SELECT timestamp, pending_violations, health_score
                FROM monitoring_snapshots
                WHERE timestamp > datetime('now', '-24 hours')
                ORDER BY timestamp
            """)
            trends = cursor.fetchall()

        return {
            "current_status": asdict(current_snapshot),
            "recent_alerts": [
                {"type": alert[0], "severity": alert[1], "message": alert[2], "timestamp": alert[3]}
                for alert in recent_alerts
            ],
            "trends": [
                {"timestamp": trend[0], "pending_violations": trend[1], "health_score": trend[2]} for trend in trends
            ],
        }

    def run_monitoring_demo(self, duration_minutes: int = 2):
        """🎮 Run monitoring demonstration"""
        lock_file = self.monitoring_dir / "monitoring.lock"
        if lock_file.exists():
            raise RuntimeError("monitoring demo already running")

        print(f"🎮 Running monitoring demo for {duration_minutes} minutes...")
        lock_file.write_text(str(os.getpid()))

        try:
            end_time = datetime.now() + timedelta(minutes=duration_minutes)

            # Take initial snapshot
            initial_snapshot = self.collect_monitoring_snapshot()
            print(
                f"📊 Initial State: {initial_snapshot.pending_violations:,} pending violations"
            )

            with tqdm(total=duration_minutes * 60, desc="# # # 🔄 Monitoring Demo", unit="s") as pbar:
                while datetime.now() < end_time:
                    start_cycle = time.time()

                    # Run monitoring cycle
                    snapshot, alerts = self.monitor_cycle()

                    if snapshot:
                        pbar.set_description(
                            f"# # # 🔄 Pending: {snapshot.pending_violations:,} | Health: {snapshot.health_score:.1f}%"
                        )

                    # Display alerts
                    for alert in alerts:
                        tqdm.write(f"# ALERT {alert['severity']}: {alert['message']}")

                    # Sleep for next cycle
                    elapsed = time.time() - start_cycle
                    sleep_time = min(
                        30, end_time.timestamp() - time.time()
                    )  # 30s max or remaining time

                    if sleep_time > 0:
                        time.sleep(sleep_time)
                        pbar.update(int(elapsed + sleep_time))

            # Final snapshot
            final_snapshot = self.collect_monitoring_snapshot()
            print(
                f"📊 Final State: {final_snapshot.pending_violations:,} pending violations"
            )

            metrics = {
                "pending_violations": float(final_snapshot.pending_violations),
                "total_violations": float(final_snapshot.total_violations),
                "health_score": float(final_snapshot.health_score),
            }
            push_metrics(metrics)
            if os.getenv("WEB_DASHBOARD_ENABLED") == "1":
                _update_dashboard(metrics)

            return {
                "initial_snapshot": initial_snapshot,
                "final_snapshot": final_snapshot,
                "demo_duration_minutes": duration_minutes,
            }
        finally:
            if lock_file.exists():
                lock_file.unlink()


def main():
    """stats" Main execution function with enterprise monitoring"""
    # MANDATORY: Start time and process tracking
    start_time = datetime.now()
    process_id = os.getpid()

    print("=" * 80)
    print("📊 CONTINUOUS MONITORING SYSTEM")
    print("=" * 80)
    print(f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Process ID: {process_id}")
    print("Target: 12,635+ violations continuous monitoring")
    print()

    try:
        # Initialize monitoring system
        monitor = ContinuousMonitoringSystem()

        # Run monitoring demo
        print("🎮 Running monitoring demonstration...")
        demo_results = monitor.run_monitoring_demo(duration_minutes=2)

        # Generate dashboard
        print("📋 Generating monitoring dashboard...")
        dashboard = monitor.get_monitoring_dashboard()

        # Save dashboard
        dashboard_file = monitor.monitoring_dir / f"dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(dashboard_file, "w", encoding="utf-8") as f:
            json.dump(dashboard, f, indent=2, default=str)

        # Success summary
        duration = (datetime.now() - start_time).total_seconds()
        print("\n" + "=" * 80)
        print("# # SUCCESS CONTINUOUS MONITORING DEMONSTRATION COMPLETED")
        print("=" * 80)
        print(f"📊 Initial Violations: {demo_results['initial_snapshot'].pending_violations:,}")
        print(f"📊 Final Violations: {demo_results['final_snapshot'].pending_violations:,}")
        print(f"📈 Health Score: {demo_results['final_snapshot'].health_score:.1f}%")
        print(f"# ALERT Recent Alerts: {len(dashboard['recent_alerts'])}")
        print(f"📋 Dashboard: {dashboard_file}")
        print(f"⏱️  Duration: {duration:.2f} seconds")
        print("=" * 80)

        # Show current status
        current = dashboard["current_status"]
        print("\n📊 CURRENT MONITORING STATUS:")
        print(f"   Pending Violations: {current['pending_violations']:,}")
        print(f"   Fixed Violations: {current['fixed_violations']:,}")
        print(f"   Files Affected: {current['files_with_violations']:,}")
        print(f"   Health Score: {current['health_score']:.1f}%")
        print(f"   Critical Violations: {current['critical_violations']:,}")

        # Show alerts if any
        if dashboard["recent_alerts"]:
            print(f"\n# ALERT RECENT ALERTS ({len(dashboard['recent_alerts'])}):")
            for alert in dashboard["recent_alerts"][:3]:
                print(f"   {alert['severity']}: {alert['message']}")

    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds()
        print(f"\n❌ ERROR: {e}")
        print(f"⏱️  Duration: {duration:.2f} seconds")
        sys.exit(1)


if __name__ == "__main__":
    main()
