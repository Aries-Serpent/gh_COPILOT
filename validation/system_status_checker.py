#!/usr/bin/env python3
"""
📊 SYSTEM STATUS CHECKER
Enterprise Health Monitoring & Validation
Database-First System Analysis

This checker provides comprehensive system health monitoring,
performance analysis, and enterprise compliance validation.
"""

import os
import sys
import sqlite3
import json
import psutil
import time
import subprocess
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import logging
from tqdm import tqdm
import socket

@dataclass
class SystemHealthMetrics:
    """System health metrics structure"""
    timestamp: str
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_connections: int
    running_processes: int
    system_uptime: str
    temperature: Optional[float] = None

@dataclass
class ServiceHealth:
    """Service health structure"""
    name: str
    status: str
    pid: Optional[int]
    port: Optional[int]
    cpu_percent: Optional[float]
    memory_mb: Optional[float]
    response_time: Optional[float]
    error_message: Optional[str]

@dataclass
class DatabaseHealth:
    """Database health structure"""
    name: str
    path: str
    size_mb: float
    table_count: int
    last_modified: str
    connectivity: bool
    error_message: Optional[str]

class SystemStatusChecker:
    """📊 Comprehensive System Status & Health Monitor"""
    
    def __init__(self):
        self.checker_id = f"STATUS_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.workspace_root = Path("E:/gh_COPILOT")
        self.production_db = self.workspace_root / "databases" / "production.db"
        self.check_time = datetime.now()
        
        # Visual indicators
        self.visual_indicators = {
            'status': '📊',
            'processing': '⚙️',
            'success': '✅',
            'error': '❌',
            'warning': '⚠️',
            'info': '📋',
            'database': '🗄️',
            'network': '🌐',
            'performance': '⚡',
            'security': '🔒'
        }
        
        # Configure logging
        self.logger = self._setup_logging()
        
        # Expected services and their ports
        self.expected_services = {
            'Enterprise Dashboard': 5000,
            'Platform Demo': 5001,
            'Web GUI Generator': 5002,
            'Template Intelligence': None,
            'Analytics Engine': None,
            'Optimization Engine': None
        }
        
        # Expected databases
        self.expected_databases = [
            'production.db',
            'enhanced_intelligence.db',
            'analytics.db',
            'monitoring.db',
            'development.db',
            'testing.db'
        ]
        
        print(f"{self.visual_indicators['status']} SYSTEM STATUS CHECKER INITIALIZED")
        print(f"Checker ID: {self.checker_id}")
        print(f"Workspace: {self.workspace_root}")
        print(f"Check Time: {self.check_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup comprehensive logging"""
        logger = logging.getLogger('system_status_checker')
        logger.setLevel(logging.INFO)
        
        # Create file handler
        log_dir = self.workspace_root / 'logs'
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / 'system_status.log'
        handler = logging.FileHandler(log_file)
        handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def check_system_health(self) -> SystemHealthMetrics:
        """Check overall system health metrics"""
        print(f"\n{self.visual_indicators['processing']} SYSTEM HEALTH CHECK")
        print("=" * 60)
        
        try:
            # Get system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Network connections
            connections = len(psutil.net_connections())
            
            # Running processes
            processes = len(psutil.pids())
            
            # System uptime
            boot_time = psutil.boot_time()
            uptime = datetime.now() - datetime.fromtimestamp(boot_time)
            uptime_str = f"{uptime.days}d {uptime.seconds//3600}h {(uptime.seconds//60)%60}m"
            
            # Temperature (if available)
            temperature = None
            try:
                # Check if sensors_temperatures exists and is available on this platform
                if hasattr(psutil, 'sensors_temperatures'):
                    sensors_func = getattr(psutil, 'sensors_temperatures')
                    if callable(sensors_func):
                        temps = sensors_func()
                        if temps:
                            # Get CPU temperature if available
                            if isinstance(temps, dict):
                                for name, entries in temps.items():
                                    if entries and len(entries) > 0:
                                        temperature = entries[0].current
                                        break
            except (AttributeError, NotImplementedError, OSError, Exception):
                # sensors_temperatures is not available on this platform (e.g., Windows)
                # or requires special permissions, or hardware doesn't support it
                pass
            
            health = SystemHealthMetrics(
                timestamp=self.check_time.isoformat(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                disk_percent=disk.percent,
                network_connections=connections,
                running_processes=processes,
                system_uptime=uptime_str,
                temperature=temperature
            )
            
            # Print health status
            print(f"{self.visual_indicators['performance']} CPU Usage: {cpu_percent:.1f}%")
            print(f"{self.visual_indicators['performance']} Memory Usage: {memory.percent:.1f}%")
            print(f"{self.visual_indicators['performance']} Disk Usage: {disk.percent:.1f}%")
            print(f"{self.visual_indicators['network']} Network Connections: {connections}")
            print(f"{self.visual_indicators['info']} Running Processes: {processes}")
            print(f"{self.visual_indicators['info']} System Uptime: {uptime_str}")
            if temperature:
                print(f"{self.visual_indicators['performance']} Temperature: {temperature:.1f}°C")
            
            return health
            
        except Exception as e:
            print(f"{self.visual_indicators['error']} System health check failed: {e}")
            self.logger.error(f"System health check failed: {e}")
            return SystemHealthMetrics(
                timestamp=self.check_time.isoformat(),
                cpu_percent=0,
                memory_percent=0,
                disk_percent=0,
                network_connections=0,
                running_processes=0,
                system_uptime="unknown"
            )
    
    def check_service_health(self) -> List[ServiceHealth]:
        """Check health of all enterprise services"""
        print(f"\n{self.visual_indicators['processing']} SERVICE HEALTH CHECK")
        print("=" * 60)
        
        services_health = []
        
        # Get all running Python processes
        python_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent', 'memory_info']):
            try:
                if proc.info['name'] and 'python' in proc.info['name'].lower():
                    python_processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Check each expected service
        for service_name, port in self.expected_services.items():
            service_health = ServiceHealth(
                name=service_name,
                status='unknown',
                pid=None,
                port=port,
                cpu_percent=None,
                memory_mb=None,
                response_time=None,
                error_message=None
            )
            
            # Check if service is running by looking for relevant processes
            service_found = False
            for proc in python_processes:
                if proc['cmdline'] and any(service_name.lower().split()[0] in ' '.join(proc['cmdline']).lower() for word in service_name.lower().split()):
                    service_found = True
                    service_health.pid = proc['pid']
                    service_health.cpu_percent = proc['cpu_percent']
                    service_health.memory_mb = proc['memory_info'].rss / 1024 / 1024 if proc['memory_info'] else None
                    service_health.status = 'running'
                    break
            
            # If service has a port, check if it's responding
            if port and service_found:
                try:
                    start_time = time.time()
                    response = requests.get(f"http://localhost:{port}/health", timeout=2)
                    service_health.response_time = time.time() - start_time
                    
                    if response.status_code == 200:
                        service_health.status = 'healthy'
                    else:
                        service_health.status = 'unhealthy'
                        service_health.error_message = f"HTTP {response.status_code}"
                        
                except requests.RequestException as e:
                    service_health.status = 'unreachable'
                    service_health.error_message = str(e)
                except Exception as e:
                    service_health.error_message = str(e)
            
            if not service_found:
                service_health.status = 'stopped'
                service_health.error_message = 'Process not found'
            
            services_health.append(service_health)
            
            # Print service status
            if service_health.status == 'healthy':
                print(f"{self.visual_indicators['success']} {service_name}: ✅ Healthy "
                      f"(PID: {service_health.pid}, Response: {service_health.response_time:.3f}s)")
            elif service_health.status == 'running':
                print(f"{self.visual_indicators['success']} {service_name}: ✅ Running "
                      f"(PID: {service_health.pid})")
            elif service_health.status == 'unhealthy':
                print(f"{self.visual_indicators['warning']} {service_name}: ⚠️ Unhealthy "
                      f"({service_health.error_message})")
            elif service_health.status == 'unreachable':
                print(f"{self.visual_indicators['error']} {service_name}: ❌ Unreachable "
                      f"({service_health.error_message})")
            else:
                print(f"{self.visual_indicators['error']} {service_name}: ❌ Stopped")
        
        return services_health
    
    def check_database_health(self) -> List[DatabaseHealth]:
        """Check health of all enterprise databases"""
        print(f"\n{self.visual_indicators['processing']} DATABASE HEALTH CHECK")
        print("=" * 60)
        
        databases_health = []
        
        # Find all database files
        db_files = []
        for db_pattern in ['*.db', '*.sqlite', '*.sqlite3']:
            db_files.extend(self.workspace_root.glob(f"**/{db_pattern}"))
        
        # Check each database
        for db_file in db_files:
            if db_file.is_file():
                db_health = DatabaseHealth(
                    name=db_file.name,
                    path=str(db_file),
                    size_mb=db_file.stat().st_size / (1024 * 1024),
                    table_count=0,
                    last_modified=datetime.fromtimestamp(db_file.stat().st_mtime).isoformat(),
                    connectivity=False,
                    error_message=None
                )
                
                # Test database connectivity
                try:
                    with sqlite3.connect(db_file) as conn:
                        cursor = conn.cursor()
                        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
                        db_health.table_count = cursor.fetchone()[0]
                        db_health.connectivity = True
                        
                        # Test a simple query
                        cursor.execute("SELECT 1")
                        cursor.fetchone()
                        
                except Exception as e:
                    db_health.error_message = str(e)
                
                databases_health.append(db_health)
                
                # Print database status
                if db_health.connectivity:
                    print(f"{self.visual_indicators['database']} {db_health.name}: ✅ Healthy "
                          f"({db_health.size_mb:.1f}MB, {db_health.table_count} tables)")
                else:
                    print(f"{self.visual_indicators['error']} {db_health.name}: ❌ Error "
                          f"({db_health.error_message})")
        
        return databases_health
    
    def check_network_connectivity(self) -> Dict[str, Any]:
        """Check network connectivity and port availability"""
        print(f"\n{self.visual_indicators['processing']} NETWORK CONNECTIVITY CHECK")
        print("=" * 60)
        
        network_status = {
            'localhost_connectivity': False,
            'external_connectivity': False,
            'port_availability': {},
            'active_connections': 0,
            'listening_ports': []
        }
        
        try:
            # Check localhost connectivity
            try:
                response = requests.get("http://localhost", timeout=2)
                network_status['localhost_connectivity'] = True
            except requests.RequestException:
                # Try to connect to localhost socket
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(2)
                    result = sock.connect_ex(('localhost', 80))
                    network_status['localhost_connectivity'] = result == 0
                    sock.close()
                except:
                    pass
            
            # Check external connectivity
            try:
                response = requests.get("https://httpbin.org/ip", timeout=5)
                network_status['external_connectivity'] = response.status_code == 200
            except requests.RequestException:
                pass
            
            # Check port availability for expected services
            for service_name, port in self.expected_services.items():
                if port:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1)
                    result = sock.connect_ex(('localhost', port))
                    network_status['port_availability'][port] = result == 0
                    sock.close()
            
            # Get active connections
            network_status['active_connections'] = len(psutil.net_connections())
            
            # Get listening ports
            for conn in psutil.net_connections(kind='inet'):
                if conn.status == 'LISTEN' and conn.laddr:
                    try:
                        port = conn.laddr.port if hasattr(conn.laddr, 'port') else conn.laddr[1]
                        network_status['listening_ports'].append(port)
                    except (AttributeError, IndexError):
                        pass
            
            # Print network status
            print(f"{self.visual_indicators['network']} Localhost: "
                  f"{'✅ Available' if network_status['localhost_connectivity'] else '❌ Unavailable'}")
            print(f"{self.visual_indicators['network']} External: "
                  f"{'✅ Available' if network_status['external_connectivity'] else '❌ Unavailable'}")
            print(f"{self.visual_indicators['network']} Active Connections: {network_status['active_connections']}")
            print(f"{self.visual_indicators['network']} Listening Ports: {sorted(set(network_status['listening_ports']))}")
            
            for port, available in network_status['port_availability'].items():
                status = '✅ In Use' if available else '❌ Available'
                print(f"{self.visual_indicators['network']} Port {port}: {status}")
            
        except Exception as e:
            print(f"{self.visual_indicators['error']} Network check failed: {e}")
            network_status['error'] = str(e)
        
        return network_status
    
    def check_disaster_recovery_status(self) -> Dict[str, Any]:
        """Check disaster recovery system status"""
        print(f"\n{self.visual_indicators['processing']} DISASTER RECOVERY STATUS")
        print("=" * 60)
        
        recovery_status = {
            'schema_initialized': False,
            'scripts_tracked': 0,
            'configurations_preserved': 0,
            'recovery_sequences': 0,
            'recovery_score': 0,
            'backup_capability': False
        }
        
        try:
            if self.production_db.exists():
                with sqlite3.connect(self.production_db) as conn:
                    cursor = conn.cursor()
                    
                    # Check if disaster recovery schema exists
                    cursor.execute("""
                        SELECT name FROM sqlite_master 
                        WHERE type='table' AND name='enhanced_script_tracking'
                    """)
                    recovery_status['schema_initialized'] = cursor.fetchone() is not None
                    
                    if recovery_status['schema_initialized']:
                        # Get tracked scripts count
                        cursor.execute("SELECT COUNT(*) FROM enhanced_script_tracking")
                        recovery_status['scripts_tracked'] = cursor.fetchone()[0]
                        
                        # Get preserved configurations count
                        cursor.execute("""
                            SELECT COUNT(*) FROM sqlite_master 
                            WHERE type='table' AND name='system_configurations'
                        """)
                        if cursor.fetchone():
                            cursor.execute("SELECT COUNT(*) FROM system_configurations")
                            recovery_status['configurations_preserved'] = cursor.fetchone()[0]
                        
                        # Get recovery sequences count
                        cursor.execute("""
                            SELECT COUNT(*) FROM sqlite_master 
                            WHERE type='table' AND name='recovery_sequences'
                        """)
                        if cursor.fetchone():
                            cursor.execute("SELECT COUNT(*) FROM recovery_sequences")
                            recovery_status['recovery_sequences'] = cursor.fetchone()[0]
                        
                        # Calculate recovery score
                        base_score = 45  # Base recovery capability
                        if recovery_status['scripts_tracked'] > 0:
                            base_score += 40
                        if recovery_status['configurations_preserved'] > 0:
                            base_score += 15
                        recovery_status['recovery_score'] = base_score
                        
                        recovery_status['backup_capability'] = recovery_status['recovery_score'] >= 85
            
            # Print recovery status
            print(f"{self.visual_indicators['security']} Schema: "
                  f"{'✅ Initialized' if recovery_status['schema_initialized'] else '❌ Not Initialized'}")
            print(f"{self.visual_indicators['security']} Scripts Tracked: {recovery_status['scripts_tracked']}")
            print(f"{self.visual_indicators['security']} Configurations: {recovery_status['configurations_preserved']}")
            print(f"{self.visual_indicators['security']} Recovery Sequences: {recovery_status['recovery_sequences']}")
            print(f"{self.visual_indicators['security']} Recovery Score: {recovery_status['recovery_score']}%")
            print(f"{self.visual_indicators['security']} Backup Capability: "
                  f"{'✅ Excellent' if recovery_status['backup_capability'] else '❌ Limited'}")
            
        except Exception as e:
            print(f"{self.visual_indicators['error']} Disaster recovery check failed: {e}")
            recovery_status['error'] = str(e)
        
        return recovery_status
    
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """Generate comprehensive system status report"""
        print(f"\n{self.visual_indicators['status']} GENERATING COMPREHENSIVE REPORT")
        print("=" * 60)
        
        # Collect all health data
        system_health = self.check_system_health()
        services_health = self.check_service_health()
        databases_health = self.check_database_health()
        network_status = self.check_network_connectivity()
        recovery_status = self.check_disaster_recovery_status()
        
        # Calculate overall health score
        health_score = 0
        max_score = 100
        
        # System health (25 points)
        if system_health.cpu_percent < 80 and system_health.memory_percent < 80:
            health_score += 25
        elif system_health.cpu_percent < 90 and system_health.memory_percent < 90:
            health_score += 15
        else:
            health_score += 5
        
        # Services health (30 points)
        healthy_services = sum(1 for s in services_health if s.status in ['healthy', 'running'])
        health_score += (healthy_services / len(services_health)) * 30
        
        # Database health (20 points)
        healthy_databases = sum(1 for d in databases_health if d.connectivity)
        if databases_health:
            health_score += (healthy_databases / len(databases_health)) * 20
        
        # Network connectivity (15 points)
        if network_status['localhost_connectivity']:
            health_score += 10
        if network_status['external_connectivity']:
            health_score += 5
        
        # Disaster recovery (10 points)
        if recovery_status['backup_capability']:
            health_score += 10
        elif recovery_status['recovery_score'] > 60:
            health_score += 5
        
        # Create comprehensive report
        report = {
            'checker_id': self.checker_id,
            'timestamp': datetime.now().isoformat(),
            'overall_health_score': round(health_score, 1),
            'system_health': asdict(system_health),
            'services_health': [asdict(s) for s in services_health],
            'databases_health': [asdict(d) for d in databases_health],
            'network_status': network_status,
            'disaster_recovery_status': recovery_status,
            'summary': {
                'healthy_services': healthy_services,
                'total_services': len(services_health),
                'healthy_databases': healthy_databases,
                'total_databases': len(databases_health),
                'network_connectivity': network_status['localhost_connectivity'],
                'disaster_recovery_ready': recovery_status['backup_capability']
            }
        }
        
        # Save report
        report_file = self.workspace_root / f"system_status_report_{self.checker_id}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report
    
    def run_comprehensive_check(self) -> Dict[str, Any]:
        """Run comprehensive system status check"""
        print(f"{self.visual_indicators['status']} COMPREHENSIVE SYSTEM STATUS CHECK")
        print("=" * 80)
        
        try:
            # Generate comprehensive report
            report = self.generate_comprehensive_report()
            
            # Print summary
            print(f"\n{self.visual_indicators['success']} SYSTEM STATUS SUMMARY")
            print("=" * 80)
            print(f"Overall Health Score: {report['overall_health_score']}/100")
            print(f"Services: {report['summary']['healthy_services']}/{report['summary']['total_services']} healthy")
            print(f"Databases: {report['summary']['healthy_databases']}/{report['summary']['total_databases']} healthy")
            print(f"Network: {'✅ Connected' if report['summary']['network_connectivity'] else '❌ Disconnected'}")
            print(f"Disaster Recovery: {'✅ Ready' if report['summary']['disaster_recovery_ready'] else '❌ Limited'}")
            print(f"Report File: system_status_report_{self.checker_id}.json")
            
            # Health assessment
            if report['overall_health_score'] >= 90:
                print(f"\n🎉 System Status: EXCELLENT")
            elif report['overall_health_score'] >= 75:
                print(f"\n✅ System Status: GOOD")
            elif report['overall_health_score'] >= 60:
                print(f"\n⚠️ System Status: FAIR")
            else:
                print(f"\n❌ System Status: NEEDS ATTENTION")
            
            return report
            
        except Exception as e:
            print(f"{self.visual_indicators['error']} System status check failed: {e}")
            self.logger.error(f"System status check failed: {e}")
            return {'error': str(e)}

def main():
    """Main system status check execution"""
    checker = SystemStatusChecker()
    report = checker.run_comprehensive_check()
    
    if 'error' not in report:
        print(f"\n📊 System status check completed successfully!")
        print(f"Health Score: {report['overall_health_score']}/100")
        
        # Provide recommendations
        if report['overall_health_score'] < 75:
            print(f"\n💡 Recommendations:")
            if report['summary']['healthy_services'] < report['summary']['total_services']:
                print("• Start missing enterprise services")
            if report['summary']['healthy_databases'] < report['summary']['total_databases']:
                print("• Check database connectivity issues")
            if not report['summary']['network_connectivity']:
                print("• Verify network configuration")
            if not report['summary']['disaster_recovery_ready']:
                print("• Run disaster recovery enhancement")
    else:
        print(f"\n❌ System status check failed")
        print(f"Error: {report['error']}")
    
    return report

if __name__ == "__main__":
    main()
