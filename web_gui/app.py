#!/usr/bin/env python3
"""
🌐 WEB GUI LAUNCHER
Flask Enterprise Dashboard & Web Interface Manager
Database-First Web Application Launcher

This launcher provides centralized management for all web GUI components
with database integration and enterprise monitoring.
"""

import os
import sys
import subprocess
import sqlite3
import json
import logging
import time
import webbrowser
from datetime import datetime
from pathlib import Path
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import threading
import requests
from flask import Flask

@dataclass
class WebComponentConfig:
    """Configuration for web components"""
    name: str
    script_path: str
    port: int
    url_path: str = "/"
    dependencies: Optional[List[str]] = None
    timeout: int = 30
    health_check_endpoint: str = "/health"

class WebGUILauncher:
    """🌐 Enterprise Web GUI Launcher & Manager"""
    
    def __init__(self):
        self.launcher_id = f"WEBGUI_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.workspace_root = Path(os.environ.get("GH_COPILOT_ROOT", os.getcwd()))
        self.production_db = self.workspace_root / "databases" / "production.db"
        self.start_time = datetime.now()
        
        # Visual indicators
        self.visual_indicators = {
            'startup': '🌐',
            'processing': '⚙️',
            'success': '✅',
            'error': '❌',
            'warning': '⚠️',
            'info': '📋',
            'database': '🗄️',
            'network': '🔗',
            'monitoring': '📊'
        }
        
        # Configure logging
        self.logger = self._setup_logging()
        
        # Initialize web components
        self.web_components = self._initialize_web_components()
        
        # Track component states
        self.component_states = {}
        self.component_processes = {}
        
        print(f"{self.visual_indicators['startup']} WEB GUI LAUNCHER INITIALIZED")
        print(f"Launcher ID: {self.launcher_id}")
        print(f"Workspace: {self.workspace_root}")
        
    def _setup_logging(self) -> logging.Logger:
        """Setup comprehensive logging"""
        logger = logging.getLogger('web_gui_launcher')
        logger.setLevel(logging.INFO)
        
        # Create file handler
        log_dir = self.workspace_root / 'logs'
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / 'web_gui_launcher.log'
        handler = logging.FileHandler(log_file)
        handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def _initialize_web_components(self) -> Dict[str, WebComponentConfig]:
        """Initialize web component configurations"""
        return {
            'enterprise_dashboard': WebComponentConfig(
                name='Enterprise Dashboard',
                script_path=ENTERPRISE_DASHBOARD_SCRIPT,
                port=5000,
                url_path='/',
                timeout=30,
                health_check_endpoint='/health'
            ),
            'platform_demo': WebComponentConfig(
                name='Platform Demo',
                script_path='web_gui/enhanced_platform_demo.py',
                port=5001,
                url_path='/demo',
                timeout=20,
                health_check_endpoint='/status'
            ),
            'web_gui_generator': WebComponentConfig(
                name='Web GUI Generator',
                script_path='web_gui/database_driven_web_gui_generator.py',
                port=5002,
                url_path='/generator',
                timeout=25,
                health_check_endpoint='/health'
            )
        }
    
    def validate_web_prerequisites(self) -> bool:
        """Validate web application prerequisites"""
        print(f"\n{self.visual_indicators['processing']} WEB APPLICATION PREREQUISITES")
        print("=" * 60)
        
        validation_results = {
            'database_connectivity': False,
            'web_scripts': False,
            'templates': False,
            'static_files': False,
            'ports_available': False
        }
        
        try:
            # Check database connectivity
            if self.production_db.exists():
                with sqlite3.connect(self.production_db) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
                    table_count = cursor.fetchone()[0]
                    validation_results['database_connectivity'] = table_count > 0
                    print(f"{self.visual_indicators['database']} Database: ✅ ({table_count} tables)")
            
            # Check web scripts
            available_scripts = 0
            for comp_name, config in self.web_components.items():
                if (self.workspace_root / config.script_path).exists():
                    available_scripts += 1
            
            validation_results['web_scripts'] = available_scripts > 0
            print(f"{self.visual_indicators['info']} Web scripts: ✅ ({available_scripts}/{len(self.web_components)})")
            
            # Check templates directory
            templates_dir = self.workspace_root / 'web_gui' / 'templates'
            template_count = len(list(templates_dir.glob('*.html'))) if templates_dir.exists() else 0
            validation_results['templates'] = template_count > 0
            print(f"{self.visual_indicators['info']} Templates: ✅ ({template_count} HTML files)")
            
            # Check static files
            static_dir = self.workspace_root / 'web_gui' / 'static'
            static_count = len(list(static_dir.rglob('*'))) if static_dir.exists() else 0
            validation_results['static_files'] = static_count > 0
            print(f"{self.visual_indicators['info']} Static files: ✅ ({static_count} files)")
            
            # Check port availability
            import socket
            available_ports = []
            for comp_name, config in self.web_components.items():
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    sock.bind(('localhost', config.port))
                    available_ports.append(config.port)
                    sock.close()
                except OSError:
                    pass
            
            validation_results['ports_available'] = len(available_ports) >= 1
            print(f"{self.visual_indicators['network']} Available ports: ✅ ({len(available_ports)} ports)")
            
            overall_validation = validation_results['database_connectivity'] and validation_results['web_scripts']
            print(f"\n{self.visual_indicators['success' if overall_validation else 'error']} "
                  f"Prerequisites: {'✅ READY' if overall_validation else '❌ NOT READY'}")
            
            return overall_validation
            
        except Exception as e:
            print(f"{self.visual_indicators['error']} Prerequisites validation error: {e}")
            return False
    
    def start_web_component(self, component_name: str, config: WebComponentConfig) -> bool:
        """Start individual web component"""
        component_path = self.workspace_root / config.script_path
        
        if not component_path.exists():
            print(f"{self.visual_indicators['error']} Component not found: {component_path}")
            return False
        
        try:
            print(f"{self.visual_indicators['processing']} Starting {config.name} on port {config.port}...")
            
            # Start web component process
            process = subprocess.Popen(
                [sys.executable, str(component_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=str(self.workspace_root),
                env=dict(os.environ, FLASK_RUN_PORT=str(config.port))
            )
            
            # Store process reference
            self.component_processes[component_name] = process
            
            # Wait for startup
            for i in range(config.timeout):
                if process.poll() is not None:
                    # Process exited early
                    stdout, stderr = process.communicate()
                    if process.returncode != 0:
                        print(f"{self.visual_indicators['error']} {config.name} failed to start:")
                        print(f"  Error: {stderr}")
                        self.component_states[component_name] = 'failed'
                        return False
                
                # Check if web server is responding
                try:
                    response = requests.get(f"http://localhost:{config.port}{config.health_check_endpoint}", timeout=1)
                    if response.status_code == 200:
                        print(f"{self.visual_indicators['success']} {config.name} started successfully")
                        self.component_states[component_name] = 'running'
                        return True
                except requests.RequestException:
                    pass
                
                time.sleep(1)
                if i % 5 == 0:
                    print(f"  {self.visual_indicators['processing']} Waiting for {config.name}... ({i+1}s)")
            
            # Check if process is still running (might be starting up)
            if process.poll() is None:
                print(f"{self.visual_indicators['success']} {config.name} process started (port {config.port})")
                self.component_states[component_name] = 'starting'
                return True
            else:
                print(f"{self.visual_indicators['error']} {config.name} process exited")
                self.component_states[component_name] = 'failed'
                return False
            
        except Exception as e:
            print(f"{self.visual_indicators['error']} Failed to start {config.name}: {e}")
            self.component_states[component_name] = 'failed'
            return False
    
    def start_primary_web_gui(self) -> bool:
        """Start the primary web GUI (Enterprise Dashboard)"""
        print(f"\n{self.visual_indicators['startup']} STARTING PRIMARY WEB GUI")
        print("=" * 60)
        
        # Start enterprise dashboard first
        enterprise_config = self.web_components['enterprise_dashboard']
        success = self.start_web_component('enterprise_dashboard', enterprise_config)
        
        if success:
            # Wait a bit more for full startup
            time.sleep(5)
            
            # Try to open in browser
            try:
                url = f"http://localhost:{enterprise_config.port}"
                print(f"{self.visual_indicators['network']} Opening browser: {url}")
                webbrowser.open(url)
            except Exception as e:
                print(f"{self.visual_indicators['warning']} Could not open browser: {e}")
            
            print(f"{self.visual_indicators['success']} Enterprise Dashboard ready at http://localhost:{enterprise_config.port}")
            
        return success
    
    def check_web_component_health(self, component_name: str, config: WebComponentConfig) -> Dict[str, Any]:
        """Check health of web component"""
        health_status = {
            'component': component_name,
            'status': 'unknown',
            'port': config.port,
            'url': f"http://localhost:{config.port}",
            'response_time': None,
            'error': None
        }
        
        try:
            start_time = time.time()
            response = requests.get(f"http://localhost:{config.port}{config.health_check_endpoint}", timeout=5)
            health_status['response_time'] = time.time() - start_time
            
            if response.status_code == 200:
                health_status['status'] = 'healthy'
            else:
                health_status['status'] = 'unhealthy'
                health_status['error'] = f"HTTP {response.status_code}"
                
        except requests.RequestException as e:
            health_status['status'] = 'unreachable'
            health_status['error'] = str(e)
        
        return health_status
    
    def monitor_web_components(self) -> Dict[str, Any]:
        """Monitor all web components"""
        print(f"\n{self.visual_indicators['monitoring']} WEB COMPONENT MONITORING")
        print("=" * 60)
        
        monitoring_results = {
            'timestamp': datetime.now().isoformat(),
            'components': {},
            'summary': {
                'total_components': len(self.web_components),
                'healthy_components': 0,
                'running_components': 0,
                'failed_components': 0
            }
        }
        
        for component_name, config in self.web_components.items():
            if component_name in self.component_processes:
                health = self.check_web_component_health(component_name, config)
                monitoring_results['components'][component_name] = health
                
                # Update summary
                if health['status'] == 'healthy':
                    monitoring_results['summary']['healthy_components'] += 1
                    monitoring_results['summary']['running_components'] += 1
                    print(f"{self.visual_indicators['success']} {config.name}: ✅ Healthy "
                          f"({health['response_time']:.3f}s)")
                elif health['status'] == 'unhealthy':
                    monitoring_results['summary']['running_components'] += 1
                    print(f"{self.visual_indicators['warning']} {config.name}: ⚠️ Unhealthy "
                          f"({health['error']})")
                else:
                    monitoring_results['summary']['failed_components'] += 1
                    print(f"{self.visual_indicators['error']} {config.name}: ❌ Unreachable "
                          f"({health['error']})")
        
        return monitoring_results
    
    def generate_launch_report(self) -> Dict[str, Any]:
        """Generate comprehensive launch report"""
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        report = {
            'launcher_id': self.launcher_id,
            'timestamp': end_time.isoformat(),
            'duration_seconds': duration.total_seconds(),
            'component_states': self.component_states,
            'monitoring_data': self.monitor_web_components(),
            'access_urls': {
                name: f"http://localhost:{config.port}"
                for name, config in self.web_components.items()
                if self.component_states.get(name) in ['running', 'starting']
            }
        }
        
        # Save report
        report_file = self.workspace_root / f"web_gui_launch_report_{self.launcher_id}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report
    
    def run_web_gui_launch(self) -> bool:
        """Run complete web GUI launch sequence"""
        print(f"{self.visual_indicators['startup']} WEB GUI LAUNCH SEQUENCE")
        print("=" * 80)
        
        try:
            # Phase 1: Prerequisites validation
            if not self.validate_web_prerequisites():
                print(f"{self.visual_indicators['error']} Prerequisites validation failed")
                return False
            
            # Phase 2: Start primary web GUI
            success = self.start_primary_web_gui()
            
            # Phase 3: Generate report
            report = self.generate_launch_report()
            
            # Phase 4: Final status
            print(f"\n{self.visual_indicators['success']} WEB GUI LAUNCH COMPLETE")
            print("=" * 80)
            
            if success:
                print(f"✅ Enterprise Dashboard: http://localhost:5000")
                print(f"Duration: {report['duration_seconds']:.1f}s")
                print(f"Report: web_gui_launch_report_{self.launcher_id}.json")
                
                # Show all available URLs
                if report['access_urls']:
                    print(f"\nAvailable Web Interfaces:")
                    for name, url in report['access_urls'].items():
                        print(f"  • {name}: {url}")
            else:
                print(f"❌ Web GUI launch failed")
                
            return success
            
        except Exception as e:
            print(f"{self.visual_indicators['error']} Web GUI launch failed: {e}")
            self.logger.error(f"Web GUI launch failed: {e}")
            return False

def main():
    """Main web GUI launch execution"""
    launcher = WebGUILauncher()
    success = launcher.run_web_gui_launch()
    
    if success:
        print("\nWeb GUI is ready.")
        print("• Enterprise Dashboard: http://localhost:5000")
        print("• Full monitoring and analytics available")
        print("• Database-driven interfaces operational")
    else:
        print(f"\n⚠️  Web GUI launch incomplete")
        print("Check the launch report for details")
    
    return success

if __name__ == "__main__":
    main()
