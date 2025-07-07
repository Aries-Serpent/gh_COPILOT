#!/usr/bin/env python3
"""
🚀 ENTERPRISE ORCHESTRATOR
Database-First System Startup & Management
DUAL COPILOT Pattern Implementation

This orchestrator provides centralized management for all enterprise systems
with database-first validation and comprehensive monitoring.
"""

import os
import sys
import subprocess
import sqlite3
import json
import logging
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from tqdm import tqdm
import psutil

@dataclass
class ServiceConfig:
    """Configuration for enterprise services"""
    name: str
    script_path: str
    port: Optional[int] = None
    dependencies: Optional[List[str]] = None
    critical: bool = True
    timeout: int = 30
    retry_count: int = 3

class EnterpriseOrchestrator:
    """🚀 Enterprise System Startup & Management Orchestrator"""
    
    def __init__(self):
        self.orchestrator_id = f"ORCHESTRATOR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.workspace_root = Path(os.environ.get("GH_COPILOT_ROOT", os.getcwd()))
        self.production_db = self.workspace_root / "databases" / "production.db"
        self.start_time = datetime.now()
        
        # Visual indicators for enterprise processing
        self.visual_indicators = {
            'startup': '🚀',
            'processing': '⚙️',
            'success': '✅',
            'error': '❌',
            'warning': '⚠️',
            'info': '📋',
            'database': '🗄️',
            'network': '🌐',
            'monitoring': '📊'
        }
        
        # Configure logging
        self.logger = self._setup_logging()
        
        # Initialize service configurations
        self.services = self._initialize_service_configurations()
        
        # Track service states
        self.service_states = {}
        self.service_processes = {}
        
        print(f"{self.visual_indicators['startup']} ENTERPRISE ORCHESTRATOR INITIALIZED")
        print(f"Orchestrator ID: {self.orchestrator_id}")
        print(f"Workspace: {self.workspace_root}")
        print(f"Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
    def _setup_logging(self) -> logging.Logger:
        """Setup comprehensive logging"""
        logger = logging.getLogger('enterprise_orchestrator')
        logger.setLevel(logging.INFO)
        
        # Create file handler
        log_file = self.workspace_root / 'orchestrator.log'
        handler = logging.FileHandler(log_file)
        handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def _initialize_service_configurations(self) -> Dict[str, ServiceConfig]:
        """Initialize enterprise service configurations"""
        return {
            'template_intelligence_platform': ServiceConfig(
                name='Template Intelligence Platform',
                script_path='core/template_intelligence_platform.py',
                critical=True,
                timeout=60
            ),
            'enterprise_dashboard': ServiceConfig(
                name='Enterprise Dashboard',
                script_path='web_gui/scripts/flask_apps/enterprise_dashboard.py',
                port=5000,
                critical=True,
                timeout=30
            ),
            'advanced_analytics': ServiceConfig(
                name='Advanced Analytics Engine',
                script_path='core/advanced_analytics_phase4_phase5_enhancement.py',
                critical=True,
                timeout=45
            ),
            'continuous_optimization': ServiceConfig(
                name='Continuous Optimization Engine',
                script_path='core/enterprise_continuous_optimization_engine.py',
                critical=True,
                timeout=30
            ),
            'performance_monitor': ServiceConfig(
                name='Performance Monitor',
                script_path='core/enterprise_performance_monitor_windows.py',
                critical=False,
                timeout=15
            ),
            'deployment_validator': ServiceConfig(
                name='Deployment Validator',
                script_path='core/final_deployment_validator.py',
                critical=False,
                timeout=20
            )
        }
    
    def validate_system_integrity(self) -> bool:
        """Validate system integrity before startup"""
        print(f"\n{self.visual_indicators['processing']} SYSTEM INTEGRITY VALIDATION")
        print("=" * 60)
        
        validation_results = {
            'database_connectivity': False,
            'essential_files': False,
            'workspace_structure': False,
            'disaster_recovery': False
        }
        
        try:
            # Check database connectivity
            if self.production_db.exists():
                with sqlite3.connect(self.production_db) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
                    table_count = cursor.fetchone()[0]
                    validation_results['database_connectivity'] = table_count > 0
                    print(f"{self.visual_indicators['database']} Database connectivity: ✅ ({table_count} tables)")
            
            # Check essential files
            essential_files = 0
            for service_name, config in self.services.items():
                if (self.workspace_root / config.script_path).exists():
                    essential_files += 1
            
            validation_results['essential_files'] = essential_files >= len(self.services) * 0.8
            print(f"{self.visual_indicators['info']} Essential files: ✅ ({essential_files}/{len(self.services)})")
            
            # Check workspace structure
            required_dirs = ['core', 'web_gui', 'scripts', 'databases', 'validation']
            existing_dirs = sum(1 for d in required_dirs if (self.workspace_root / d).exists())
            validation_results['workspace_structure'] = existing_dirs >= len(required_dirs) * 0.8
            print(f"{self.visual_indicators['info']} Workspace structure: ✅ ({existing_dirs}/{len(required_dirs)})")
            
            # Check disaster recovery capability
            if self.production_db.exists():
                with sqlite3.connect(self.production_db) as conn:
                    cursor = conn.cursor()
                    try:
                        cursor.execute("SELECT COUNT(*) FROM enhanced_script_tracking")
                        recovery_count = cursor.fetchone()[0]
                        validation_results['disaster_recovery'] = recovery_count > 0
                        print(f"{self.visual_indicators['success']} Disaster recovery: ✅ ({recovery_count} scripts tracked)")
                    except sqlite3.OperationalError:
                        print(f"{self.visual_indicators['warning']} Disaster recovery: ⚠️ (Schema not initialized)")
            
            overall_validation = all(validation_results.values())
            print(f"\n{self.visual_indicators['success' if overall_validation else 'error']} "
                  f"System integrity: {'✅ PASSED' if overall_validation else '❌ FAILED'}")
            
            return overall_validation
            
        except Exception as e:
            print(f"{self.visual_indicators['error']} System validation error: {e}")
            return False
    
    def start_service(self, service_name: str, config: ServiceConfig) -> bool:
        """Start individual enterprise service"""
        service_path = self.workspace_root / config.script_path
        
        if not service_path.exists():
            print(f"{self.visual_indicators['error']} Service not found: {service_path}")
            return False
        
        try:
            print(f"{self.visual_indicators['processing']} Starting {config.name}...")
            
            # Start service process
            process = subprocess.Popen(
                [sys.executable, str(service_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=str(self.workspace_root)
            )
            
            # Store process reference
            self.service_processes[service_name] = process
            
            # Wait for startup (with timeout)
            startup_timeout = config.timeout
            for i in range(startup_timeout):
                if process.poll() is not None:
                    # Process exited
                    stdout, stderr = process.communicate()
                    if process.returncode == 0:
                        print(f"{self.visual_indicators['success']} {config.name} started successfully")
                        self.service_states[service_name] = 'running'
                        return True
                    else:
                        print(f"{self.visual_indicators['error']} {config.name} startup failed:")
                        print(f"  Error: {stderr}")
                        self.service_states[service_name] = 'failed'
                        return False
                
                time.sleep(1)
                if i % 5 == 0:
                    print(f"  {self.visual_indicators['processing']} Waiting for {config.name}... ({i+1}s)")
            
            # Service is still running (background service)
            print(f"{self.visual_indicators['success']} {config.name} is running in background")
            self.service_states[service_name] = 'running'
            return True
            
        except Exception as e:
            print(f"{self.visual_indicators['error']} Failed to start {config.name}: {e}")
            self.service_states[service_name] = 'failed'
            return False
    
    def start_all_services(self) -> Dict[str, bool]:
        """Start all enterprise services in order"""
        print(f"\n{self.visual_indicators['startup']} STARTING ALL ENTERPRISE SERVICES")
        print("=" * 60)
        
        startup_results = {}
        
        # Start services in dependency order
        service_order = [
            'template_intelligence_platform',
            'continuous_optimization',
            'advanced_analytics',
            'enterprise_dashboard',
            'performance_monitor',
            'deployment_validator'
        ]
        
        with tqdm(total=len(service_order), desc="Starting Services") as pbar:
            for service_name in service_order:
                if service_name in self.services:
                    config = self.services[service_name]
                    result = self.start_service(service_name, config)
                    startup_results[service_name] = result
                    
                    if not result and config.critical:
                        print(f"{self.visual_indicators['error']} Critical service {service_name} failed to start")
                        break
                    
                    pbar.update(1)
                    time.sleep(2)  # Brief pause between services
        
        return startup_results
    
    def monitor_services(self) -> Dict[str, Any]:
        """Monitor all running services"""
        print(f"\n{self.visual_indicators['monitoring']} SERVICE MONITORING")
        print("=" * 60)
        
        monitoring_results = {
            'timestamp': datetime.now().isoformat(),
            'services': {},
            'system_health': {}
        }
        
        # Check each service
        for service_name, process in self.service_processes.items():
            if process:
                status = {
                    'running': process.poll() is None,
                    'pid': process.pid if process.poll() is None else None,
                    'cpu_percent': None,
                    'memory_mb': None
                }
                
                # Get process metrics if running
                if status['running']:
                    try:
                        proc = psutil.Process(process.pid)
                        status['cpu_percent'] = proc.cpu_percent()
                        status['memory_mb'] = proc.memory_info().rss / 1024 / 1024
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        status['running'] = False
                
                monitoring_results['services'][service_name] = status
                
                # Print status
                if status['running']:
                    print(f"{self.visual_indicators['success']} {service_name}: Running "
                          f"(PID: {status['pid']}, CPU: {status['cpu_percent']:.1f}%, "
                          f"Memory: {status['memory_mb']:.1f}MB)")
                else:
                    print(f"{self.visual_indicators['error']} {service_name}: Not running")
        
        # System health metrics
        monitoring_results['system_health'] = {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent,
            'running_services': sum(1 for s in monitoring_results['services'].values() if s['running'])
        }
        
        print(f"\n{self.visual_indicators['monitoring']} System Health:")
        health = monitoring_results['system_health']
        print(f"  CPU: {health['cpu_percent']:.1f}%")
        print(f"  Memory: {health['memory_percent']:.1f}%")
        print(f"  Disk: {health['disk_percent']:.1f}%")
        print(f"  Services: {health['running_services']}/{len(self.services)}")
        
        return monitoring_results
    
    def generate_startup_report(self, startup_results: Dict[str, bool]) -> Dict[str, Any]:
        """Generate comprehensive startup report"""
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        report = {
            'orchestrator_id': self.orchestrator_id,
            'timestamp': end_time.isoformat(),
            'duration_seconds': duration.total_seconds(),
            'startup_results': startup_results,
            'services_started': sum(1 for result in startup_results.values() if result),
            'total_services': len(startup_results),
            'success_rate': sum(1 for result in startup_results.values() if result) / len(startup_results) * 100,
            'system_ready': all(startup_results.get(s, False) for s in ['template_intelligence_platform', 'enterprise_dashboard']),
            'monitoring_data': self.monitor_services()
        }
        
        # Save report
        report_file = self.workspace_root / f"startup_report_{self.orchestrator_id}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report
    
    def run_orchestration(self) -> bool:
        """Run complete enterprise orchestration"""
        print(f"{self.visual_indicators['startup']} ENTERPRISE ORCHESTRATION INITIATED")
        print("=" * 80)
        
        try:
            # Phase 1: System validation
            if not self.validate_system_integrity():
                print(f"{self.visual_indicators['error']} System validation failed - aborting startup")
                return False
            
            # Phase 2: Service startup
            startup_results = self.start_all_services()
            
            # Phase 3: Generate report
            report = self.generate_startup_report(startup_results)
            
            # Phase 4: Final status
            print(f"\n{self.visual_indicators['success']} ENTERPRISE ORCHESTRATION COMPLETE")
            print("=" * 80)
            print(f"Services Started: {report['services_started']}/{report['total_services']}")
            print(f"Success Rate: {report['success_rate']:.1f}%")
            print(f"System Ready: {'✅ YES' if report['system_ready'] else '❌ NO'}")
            print(f"Duration: {report['duration_seconds']:.1f}s")
            print(f"Report: startup_report_{self.orchestrator_id}.json")
            
            return report['system_ready']
            
        except Exception as e:
            print(f"{self.visual_indicators['error']} Orchestration failed: {e}")
            self.logger.error(f"Orchestration failed: {e}")
            return False

def main():
    """Main orchestration execution"""
    orchestrator = EnterpriseOrchestrator()
    success = orchestrator.run_orchestration()
    
    if success:
        print(f"\n🎉 Enterprise system is ready for operation!")
        print("Available services:")
        print("  - Template Intelligence Platform: Core system intelligence")
        print("  - Enterprise Dashboard: http://localhost:5000")
        print("  - Advanced Analytics: Phase 4 & 5 capabilities")
        print("  - Continuous Optimization: 24/7 monitoring")
    else:
        print(f"\n⚠️  Enterprise system startup incomplete")
        print("Check the startup report for details")
    
    return success

if __name__ == "__main__":
    main()
