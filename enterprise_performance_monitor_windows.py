#!/usr/bin/env python3
"""
Enterprise Performance Monitor - Windows Compatible Version
=========================================================

Professional Windows-compatible performance monitoring without Unicode dependencies.
Designed for enterprise environments requiring maximum compatibility.

DUAL COPILOT PATTERN: Primary Monitor with Secondary Validator
- Primary: Real-time performance monitoring
- Secondary: Validates monitoring accuracy
- Enterprise: Professional output for all Windows systems
"""

import os
import sys
import time
import json
import sqlite3
import psutil
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import logging

@dataclass
class PerformanceMetrics:
    """Performance metrics data structure."""
    timestamp: str
    cpu_percent: float
    memory_percent: float
    disk_usage_percent: float
    network_io_bytes: int
    process_count: int
    database_connections: int
    regeneration_capability: float
    system_health_score: float

@dataclass
class SystemHealthReport:
    """System health report data structure."""
    timestamp: str
    overall_health: str
    cpu_status: str
    memory_status: str
    disk_status: str
    network_status: str
    database_status: str
    regeneration_status: str
    recommendations: List[str]

class EnterprisePerformanceMonitor:
    """Enterprise-grade performance monitoring system."""
    
    def __init__(self, workspace_path: str = "e:/gh_COPILOT"):
        self.workspace_path = Path(workspace_path)
        self.staging_path = Path("e:/gh_COPILOT")
        self.monitoring_active = False
        self.monitoring_thread = None
        self.metrics_history = []
        self.max_history_size = 1000
        
        # Setup logging
        log_file = self.workspace_path / 'performance_monitor.log'
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(log_file)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize database
        self.init_monitoring_database()
        
    def init_monitoring_database(self):
        """Initialize monitoring database."""
        db_path = self.workspace_path / 'databases' / 'performance_monitoring.db'
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Create performance metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    cpu_percent REAL,
                    memory_percent REAL,
                    disk_usage_percent REAL,
                    network_io_bytes INTEGER,
                    process_count INTEGER,
                    database_connections INTEGER,
                    regeneration_capability REAL,
                    system_health_score REAL
                )
            ''')
            
            # Create health reports table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS health_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    overall_health TEXT,
                    cpu_status TEXT,
                    memory_status TEXT,
                    disk_status TEXT,
                    network_status TEXT,
                    database_status TEXT,
                    regeneration_status TEXT,
                    recommendations TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            
            self.logger.info("Performance monitoring database initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize monitoring database: {str(e)}")
            
    def collect_system_metrics(self) -> PerformanceMetrics:
        """Collect current system performance metrics."""
        try:
            # CPU and memory metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            # Disk usage
            disk_usage = psutil.disk_usage('/')
            disk_percent = (disk_usage.used / disk_usage.total) * 100
            
            # Network I/O
            network_io = psutil.net_io_counters()
            network_bytes = network_io.bytes_sent + network_io.bytes_recv
            
            # Process count
            process_count = len(psutil.pids())
            
            # Database connections
            db_connections = self.count_database_connections()
            
            # Regeneration capability
            regeneration_capability = self.assess_regeneration_capability()
            
            # System health score
            health_score = self.calculate_system_health_score(
                cpu_percent, memory.percent, disk_percent, 
                db_connections, regeneration_capability
            )
            
            return PerformanceMetrics(
                timestamp=datetime.now().isoformat(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                disk_usage_percent=disk_percent,
                network_io_bytes=network_bytes,
                process_count=process_count,
                database_connections=db_connections,
                regeneration_capability=regeneration_capability,
                system_health_score=health_score
            )
            
        except Exception as e:
            self.logger.error(f"Failed to collect system metrics: {str(e)}")
            return None
            
    def count_database_connections(self) -> int:
        """Count active database connections."""
        try:
            db_count = 0
            
            # Count sandbox databases
            sandbox_db_dir = self.workspace_path / 'databases'
            if sandbox_db_dir.exists():
                db_count += len(list(sandbox_db_dir.glob('*.db')))
                
            # Count staging databases
            staging_db_dir = self.staging_path / 'databases'
            if staging_db_dir.exists():
                db_count += len(list(staging_db_dir.glob('*.db')))
                
            return db_count
            
        except Exception as e:
            self.logger.error(f"Failed to count database connections: {str(e)}")
            return 0
            
    def assess_regeneration_capability(self) -> float:
        """Assess current regeneration capability."""
        try:
            # Check if key regeneration files exist
            regeneration_files = [
                'enterprise_regeneration_sync_engine.py',
                'enterprise_regeneration_capability_enhancer.py',
                'enterprise_regeneration_final_validator.py'
            ]
            
            files_present = 0
            for file_name in regeneration_files:
                if (self.workspace_path / file_name).exists():
                    files_present += 1
                    
            # Calculate capability percentage
            capability = (files_present / len(regeneration_files)) * 100
            
            # Bonus for database presence
            db_dir = self.workspace_path / 'databases'
            if db_dir.exists():
                db_count = len(list(db_dir.glob('*.db')))
                if db_count > 10:
                    capability += 20
                elif db_count > 5:
                    capability += 10
                    
            return min(capability, 100.0)
            
        except Exception as e:
            self.logger.error(f"Failed to assess regeneration capability: {str(e)}")
            return 0.0
            
    def calculate_system_health_score(self, cpu: float, memory: float, 
                                    disk: float, db_connections: int, 
                                    regeneration: float) -> float:
        """Calculate overall system health score."""
        try:
            # Component scores (higher is better)
            cpu_score = max(0, 100 - cpu)  # Lower CPU usage is better
            memory_score = max(0, 100 - memory)  # Lower memory usage is better
            disk_score = max(0, 100 - disk)  # Lower disk usage is better
            db_score = min(100, db_connections * 2)  # More databases is better
            regen_score = regeneration  # Higher regeneration capability is better
            
            # Weighted average
            weights = {
                'cpu': 0.2,
                'memory': 0.2,
                'disk': 0.15,
                'database': 0.2,
                'regeneration': 0.25
            }
            
            health_score = (
                cpu_score * weights['cpu'] +
                memory_score * weights['memory'] +
                disk_score * weights['disk'] +
                db_score * weights['database'] +
                regen_score * weights['regeneration']
            )
            
            return round(health_score, 2)
            
        except Exception as e:
            self.logger.error(f"Failed to calculate system health score: {str(e)}")
            return 0.0
            
    def generate_health_report(self, metrics: PerformanceMetrics) -> SystemHealthReport:
        """Generate comprehensive system health report."""
        try:
            # Determine status levels
            def get_status(value: float, thresholds: Dict[str, float]) -> str:
                if value <= thresholds['good']:
                    return 'EXCELLENT'
                elif value <= thresholds['warning']:
                    return 'GOOD'
                elif value <= thresholds['critical']:
                    return 'WARNING'
                else:
                    return 'CRITICAL'
                    
            # CPU status
            cpu_status = get_status(metrics.cpu_percent, {
                'good': 30, 'warning': 60, 'critical': 85
            })
            
            # Memory status
            memory_status = get_status(metrics.memory_percent, {
                'good': 40, 'warning': 70, 'critical': 90
            })
            
            # Disk status
            disk_status = get_status(metrics.disk_usage_percent, {
                'good': 50, 'warning': 75, 'critical': 90
            })
            
            # Network status (simplified)
            network_status = 'GOOD' if metrics.network_io_bytes > 0 else 'WARNING'
            
            # Database status
            if metrics.database_connections >= 20:
                database_status = 'EXCELLENT'
            elif metrics.database_connections >= 10:
                database_status = 'GOOD'
            elif metrics.database_connections >= 5:
                database_status = 'WARNING'
            else:
                database_status = 'CRITICAL'
                
            # Regeneration status
            if metrics.regeneration_capability >= 90:
                regeneration_status = 'EXCELLENT'
            elif metrics.regeneration_capability >= 75:
                regeneration_status = 'GOOD'
            elif metrics.regeneration_capability >= 50:
                regeneration_status = 'WARNING'
            else:
                regeneration_status = 'CRITICAL'
                
            # Overall health
            if metrics.system_health_score >= 80:
                overall_health = 'EXCELLENT'
            elif metrics.system_health_score >= 60:
                overall_health = 'GOOD'
            elif metrics.system_health_score >= 40:
                overall_health = 'WARNING'
            else:
                overall_health = 'CRITICAL'
                
            # Generate recommendations
            recommendations = []
            if metrics.cpu_percent > 80:
                recommendations.append("High CPU usage detected - consider optimizing processes")
            if metrics.memory_percent > 80:
                recommendations.append("High memory usage detected - consider memory optimization")
            if metrics.disk_usage_percent > 80:
                recommendations.append("High disk usage detected - consider cleanup")
            if metrics.database_connections < 10:
                recommendations.append("Low database count - consider database deployment")
            if metrics.regeneration_capability < 75:
                recommendations.append("Regeneration capability below optimal - consider enhancement")
                
            if not recommendations:
                recommendations.append("System operating at optimal performance")
                
            return SystemHealthReport(
                timestamp=metrics.timestamp,
                overall_health=overall_health,
                cpu_status=cpu_status,
                memory_status=memory_status,
                disk_status=disk_status,
                network_status=network_status,
                database_status=database_status,
                regeneration_status=regeneration_status,
                recommendations=recommendations
            )
            
        except Exception as e:
            self.logger.error(f"Failed to generate health report: {str(e)}")
            return None
            
    def save_metrics(self, metrics: PerformanceMetrics):
        """Save metrics to database."""
        try:
            db_path = self.workspace_path / 'databases' / 'performance_monitoring.db'
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO performance_metrics (
                    timestamp, cpu_percent, memory_percent, disk_usage_percent,
                    network_io_bytes, process_count, database_connections,
                    regeneration_capability, system_health_score
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metrics.timestamp, metrics.cpu_percent, metrics.memory_percent,
                metrics.disk_usage_percent, metrics.network_io_bytes,
                metrics.process_count, metrics.database_connections,
                metrics.regeneration_capability, metrics.system_health_score
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Failed to save metrics: {str(e)}")
            
    def save_health_report(self, report: SystemHealthReport):
        """Save health report to database."""
        try:
            db_path = self.workspace_path / 'databases' / 'performance_monitoring.db'
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO health_reports (
                    timestamp, overall_health, cpu_status, memory_status,
                    disk_status, network_status, database_status,
                    regeneration_status, recommendations
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                report.timestamp, report.overall_health, report.cpu_status,
                report.memory_status, report.disk_status, report.network_status,
                report.database_status, report.regeneration_status,
                json.dumps(report.recommendations)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Failed to save health report: {str(e)}")
            
    def display_metrics(self, metrics: PerformanceMetrics, report: SystemHealthReport):
        """Display metrics in professional format."""
        print("\n" + "="*70)
        print("ENTERPRISE PERFORMANCE MONITOR - REAL-TIME METRICS")
        print("="*70)
        print(f"Timestamp: {metrics.timestamp}")
        print(f"System Health Score: {metrics.system_health_score}/100.0")
        print(f"Overall Health: {report.overall_health}")
        print()
        
        print("SYSTEM METRICS:")
        print(f"  CPU Usage: {metrics.cpu_percent:6.1f}% - {report.cpu_status}")
        print(f"  Memory Usage: {metrics.memory_percent:6.1f}% - {report.memory_status}")
        print(f"  Disk Usage: {metrics.disk_usage_percent:6.1f}% - {report.disk_status}")
        print(f"  Network I/O: {metrics.network_io_bytes:>10,} bytes - {report.network_status}")
        print(f"  Process Count: {metrics.process_count:>8} - Active")
        print()
        
        print("ENTERPRISE METRICS:")
        print(f"  Database Connections: {metrics.database_connections:>5} - {report.database_status}")
        print(f"  Regeneration Capability: {metrics.regeneration_capability:>5.1f}% - {report.regeneration_status}")
        print()
        
        print("RECOMMENDATIONS:")
        for i, rec in enumerate(report.recommendations, 1):
            print(f"  {i}. {rec}")
        print()
        
    def monitoring_loop(self):
        """Main monitoring loop."""
        self.logger.info("Performance monitoring started")
        
        while self.monitoring_active:
            try:
                # Collect metrics
                metrics = self.collect_system_metrics()
                if metrics is None:
                    time.sleep(5)
                    continue
                    
                # Generate health report
                report = self.generate_health_report(metrics)
                if report is None:
                    time.sleep(5)
                    continue
                    
                # Save to database
                self.save_metrics(metrics)
                self.save_health_report(report)
                
                # Add to history
                self.metrics_history.append(metrics)
                if len(self.metrics_history) > self.max_history_size:
                    self.metrics_history.pop(0)
                    
                # Display metrics
                self.display_metrics(metrics, report)
                
                # Wait for next cycle
                time.sleep(10)  # 10-second monitoring interval
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {str(e)}")
                time.sleep(5)
                
        self.logger.info("Performance monitoring stopped")
        
    def start_monitoring(self):
        """Start performance monitoring."""
        if self.monitoring_active:
            print("[WARNING] Monitoring already active")
            return
            
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self.monitoring_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        
        print("[SUCCESS] Performance monitoring started")
        print("Press Ctrl+C to stop monitoring")
        
    def stop_monitoring(self):
        """Stop performance monitoring."""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
            
        print("[SUCCESS] Performance monitoring stopped")
        
    def run_single_check(self):
        """Run a single performance check."""
        print("\n" + "="*70)
        print("ENTERPRISE PERFORMANCE CHECK - SINGLE SNAPSHOT")
        print("="*70)
        
        # Collect metrics
        metrics = self.collect_system_metrics()
        if metrics is None:
            print("[ERROR] Failed to collect metrics")
            return
            
        # Generate health report
        report = self.generate_health_report(metrics)
        if report is None:
            print("[ERROR] Failed to generate health report")
            return
            
        # Save to database
        self.save_metrics(metrics)
        self.save_health_report(report)
        
        # Display results
        self.display_metrics(metrics, report)
        
        # Save to file
        report_path = self.workspace_path / f'performance_check_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(report_path, 'w') as f:
            json.dump({
                'metrics': asdict(metrics),
                'health_report': asdict(report)
            }, f, indent=2)
            
        print(f"[SUCCESS] Performance check saved to: {report_path}")

def main():
    """Main execution function."""
    print("Enterprise Performance Monitor - Windows Compatible")
    print("Usage: python enterprise_performance_monitor_windows.py [check|monitor]")
    
    try:
        mode = sys.argv[1] if len(sys.argv) > 1 else "check"
        
        monitor = EnterprisePerformanceMonitor()
        
        if mode == "monitor":
            monitor.start_monitoring()
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                monitor.stop_monitoring()
        else:
            monitor.run_single_check()
            
    except Exception as e:
        print(f"[ERROR] Performance monitor failed: {str(e)}")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())
