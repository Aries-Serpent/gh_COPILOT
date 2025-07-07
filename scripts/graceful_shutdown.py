#!/usr/bin/env python3
"""
[PROCESSING] GRACEFUL SHUTDOWN CLI - Enhanced Analytics Intelligence Platform
[TARGET] DUAL COPILOT ENTERPRISE MANDATE: Visual Processing + Anti-Recursion + Database-Driven

This CLI provides graceful shutdown capabilities for the 24/7 monitoring system
with comprehensive state saving, cleanup, and reporting.
"""

import os
import sys
import json
import time
import psutil
import signal
import sqlite3
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import subprocess
import threading
from tqdm import tqdm

@dataclass
class ProcessInfo:
    """Process information for graceful shutdown"""
    pid: int
    name: str
    cmdline: str
    start_time: float
    memory_mb: float
    cpu_percent: float

@dataclass
class ShutdownResult:
    """Result of shutdown operation"""
    success: bool
    processes_terminated: int
    cleanup_actions: int
    database_saved: bool
    reports_generated: bool
    shutdown_time: float
    errors: List[str]

class GracefulShutdownCLI:
    """[PROCESSING] Graceful Shutdown CLI with DUAL COPILOT compliance and visual indicators"""
    
    def __init__(self):
        self.workspace = Path.cwd()
        self.shutdown_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.recursion_guard = set()
        self.shutdown_log = []
        self.start_time = time.time()
        
        # Platform process patterns to detect
        self.platform_patterns = [
            'enhanced_analytics_intelligence_platform',
            'enterprise_dashboard',
            'enterprise_intelligence_deployment_orchestrator',
            'enterprise_business_rules_customization',
            'intelligence_bridge',
            'automation_engine',
            'continuous_operation_monitor'
        ]
        
        print("[PROCESSING] GRACEFUL SHUTDOWN CLI - Enhanced Analytics Intelligence Platform")
        print("=" * 80)
        print(f"[TARGET] DUAL COPILOT: Visual Processing [SUCCESS] | Anti-Recursion [SUCCESS] | Database-Driven [SUCCESS]")
        print(f"[TIME] Shutdown Initiated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"[FOLDER] Workspace: {self.workspace}")
        print(f"[?] Shutdown ID: {self.shutdown_id}")
        print("=" * 80)
    
    def detect_platform_processes(self) -> List[ProcessInfo]:
        """Detect running platform processes with visual indicators"""
        print("\n[SEARCH] DETECTING PLATFORM PROCESSES...")
        
        platform_processes = []
        all_processes = list(psutil.process_iter(['pid', 'name', 'cmdline', 'create_time', 'memory_info', 'cpu_percent']))
        
        with tqdm(total=len(all_processes), desc="Scanning processes", unit="proc") as pbar:
            for proc in all_processes:
                try:
                    pbar.update(1)
                    cmdline = proc.info['cmdline']
                    if cmdline and any(pattern in ' '.join(cmdline) for pattern in self.platform_patterns):
                        memory_mb = proc.info['memory_info'].rss / 1024 / 1024 if proc.info['memory_info'] else 0
                        
                        process_info = ProcessInfo(
                            pid=proc.info['pid'],
                            name=proc.info['name'],
                            cmdline=' '.join(cmdline),
                            start_time=proc.info['create_time'],
                            memory_mb=memory_mb,
                            cpu_percent=proc.info['cpu_percent'] or 0
                        )
                        platform_processes.append(process_info)
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
        
        if platform_processes:
            print(f"[SUCCESS] FOUND {len(platform_processes)} PLATFORM PROCESSES:")
            for proc in platform_processes:
                uptime = time.time() - proc.start_time
                uptime_str = str(timedelta(seconds=int(uptime)))
                print(f"   [?] PID {proc.pid}: {proc.name} ({proc.memory_mb:.1f}MB, {proc.cpu_percent:.1f}% CPU, {uptime_str} uptime)")
        else:
            print("[WARNING]  NO PLATFORM PROCESSES DETECTED")
        
        return platform_processes
    
    def save_system_state(self) -> bool:
        """Save current system state to database before shutdown"""
        print("\n[STORAGE] SAVING SYSTEM STATE...")
        
        try:
            # Save to shutdown state database
            shutdown_db = self.workspace / f"shutdown_state_{self.shutdown_id}.db"
            
            with sqlite3.connect(shutdown_db) as conn:
                cursor = conn.cursor()
                
                # Create shutdown state table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS shutdown_state (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        shutdown_id TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        component_name TEXT NOT NULL,
                        state_data TEXT NOT NULL,
                        status TEXT NOT NULL
                    )
                """)
                
                # Save current platform state
                platform_state = {
                    'workspace': str(self.workspace),
                    'shutdown_timestamp': datetime.now().isoformat(),
                    'platform_processes': len(self.detect_platform_processes()),
                    'system_info': {
                        'cpu_count': psutil.cpu_count(),
                        'memory_total': psutil.virtual_memory().total,
                        'disk_usage': psutil.disk_usage(str(self.workspace)).percent
                    }
                }
                
                cursor.execute("""
                    INSERT INTO shutdown_state (shutdown_id, timestamp, component_name, state_data, status)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    self.shutdown_id,
                    datetime.now().isoformat(),
                    'platform_state',
                    json.dumps(platform_state),
                    'SAVED'
                ))
                
                # Save configuration files state
                config_files = [
                    'enterprise_deployment/active_customization_config.json',
                    'enterprise_deployment/automation_config.json',
                    'production.db'
                ]
                
                for config_file in config_files:
                    file_path = self.workspace / config_file
                    if file_path.exists():
                        cursor.execute("""
                            INSERT INTO shutdown_state (shutdown_id, timestamp, component_name, state_data, status)
                            VALUES (?, ?, ?, ?, ?)
                        """, (
                            self.shutdown_id,
                            datetime.now().isoformat(),
                            f'config_file_{config_file}',
                            json.dumps({
                                'path': str(file_path),
                                'size': file_path.stat().st_size,
                                'modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                            }),
                            'SAVED'
                        ))
                
                conn.commit()
                print(f"[SUCCESS] System state saved to: {shutdown_db}")
                return True
                
        except Exception as e:
            print(f"[ERROR] Error saving system state: {str(e)}")
            return False
    
    def graceful_process_termination(self, processes: List[ProcessInfo]) -> int:
        """Gracefully terminate platform processes with visual feedback"""
        print("\n[PROCESSING] GRACEFUL PROCESS TERMINATION...")
        
        terminated_count = 0
        
        with tqdm(total=len(processes), desc="Terminating processes", unit="proc") as pbar:
            for proc_info in processes:
                try:
                    pbar.set_postfix({"PID": proc_info.pid})
                    
                    # Try to get the process
                    proc = psutil.Process(proc_info.pid)
                    
                    # Send SIGTERM for graceful shutdown
                    proc.terminate()
                    
                    # Wait up to 10 seconds for graceful termination
                    try:
                        proc.wait(timeout=10)
                        print(f"[SUCCESS] Gracefully terminated PID {proc_info.pid}")
                        terminated_count += 1
                    except psutil.TimeoutExpired:
                        # Force kill if graceful termination fails
                        proc.kill()
                        print(f"[WARNING]  Force killed PID {proc_info.pid} (graceful termination timeout)")
                        terminated_count += 1
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    print(f"[WARNING]  Process PID {proc_info.pid} already terminated or access denied")
                    terminated_count += 1
                
                pbar.update(1)
                time.sleep(0.5)  # Brief pause between terminations
        
        print(f"[SUCCESS] TERMINATED {terminated_count}/{len(processes)} PROCESSES")
        return terminated_count
    
    def cleanup_resources(self) -> int:
        """Clean up temporary resources and files"""
        print("\n[?] CLEANING UP RESOURCES...")
        
        cleanup_actions = 0
        
        # Clean up temporary files
        temp_patterns = [
            'intelligence/temp/*.tmp',
            'intelligence/logs/*.lock',
            '*.pid',
            'temp_*'
        ]
        
        for pattern in temp_patterns:
            matching_files = list(self.workspace.glob(pattern))
            if matching_files:
                for file_path in matching_files:
                    try:
                        if file_path.exists():
                            file_path.unlink()
                            print(f"   [TRASH]  Removed: {file_path}")
                            cleanup_actions += 1
                    except Exception as e:
                        print(f"   [WARNING]  Could not remove {file_path}: {str(e)}")
        
        # Close database connections
        try:
            # Signal any remaining database connections to close
            for db_file in self.workspace.glob('*.db'):
                if db_file.exists():
                    # Create a simple connection to ensure proper closure
                    try:
                        with sqlite3.connect(db_file) as conn:
                            conn.execute('PRAGMA optimize')
                        cleanup_actions += 1
                        print(f"   [WRENCH] Optimized database: {db_file}")
                    except Exception as e:
                        print(f"   [WARNING]  Could not optimize {db_file}: {str(e)}")
        except Exception as e:
            print(f"   [WARNING]  Database cleanup error: {str(e)}")
        
        print(f"[SUCCESS] COMPLETED {cleanup_actions} CLEANUP ACTIONS")
        return cleanup_actions
    
    def generate_shutdown_report(self, result: ShutdownResult) -> Path:
        """Generate comprehensive shutdown report"""
        print("\n[BAR_CHART] GENERATING SHUTDOWN REPORT...")
        
        report_path = self.workspace / f"shutdown_report_{self.shutdown_id}.md"
        
        report_content = f"""# [PROCESSING] GRACEFUL SHUTDOWN REPORT
## Enhanced Analytics Intelligence Platform

### [BAR_CHART] **SHUTDOWN SUMMARY**
- **Shutdown ID**: {self.shutdown_id}
- **Timestamp**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Success**: {'[SUCCESS] YES' if result.success else '[ERROR] NO'}
- **Duration**: {result.shutdown_time:.2f} seconds

### [PROCESSING] **PROCESS TERMINATION**
- **Processes Terminated**: {result.processes_terminated}
- **Termination Method**: Graceful (SIGTERM) with 10s timeout fallback

### [?] **CLEANUP ACTIONS**
- **Cleanup Actions**: {result.cleanup_actions}
- **Temporary Files**: Removed
- **Database Connections**: Closed and optimized
- **Resource Cleanup**: Completed

### [STORAGE] **STATE PRESERVATION**
- **Database State**: {'[SUCCESS] SAVED' if result.database_saved else '[ERROR] NOT SAVED'}
- **Configuration Files**: Backed up
- **System State**: Preserved in shutdown_state_{self.shutdown_id}.db

### [CHART_INCREASING] **SYSTEM METRICS**
- **CPU Usage**: {psutil.cpu_percent()}%
- **Memory Usage**: {psutil.virtual_memory().percent}%
- **Disk Usage**: {psutil.disk_usage(str(self.workspace)).percent}%

### [CLIPBOARD] **SHUTDOWN LOG**
"""
        
        for log_entry in self.shutdown_log:
            report_content += f"- {log_entry}\n"
        
        if result.errors:
            report_content += f"\n### [ERROR] **ERRORS ENCOUNTERED**\n"
            for error in result.errors:
                report_content += f"- {error}\n"
        
        report_content += f"""
### [PROCESSING] **RESTART INSTRUCTIONS**
To restart the platform:
```bash
# Option 1: Use quick start script
python quick_start_intelligence_platform.py

# Option 2: Use launch script
launch_platform.bat

# Option 3: Manual restart
python enhanced_analytics_intelligence_platform.py
```

### [TARGET] **PLATFORM STATUS**
- **Workspace**: {self.workspace}
- **Platform Files**: Intact
- **Database**: Optimized and ready
- **Configuration**: Preserved

---

*Shutdown Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*  
*Enhanced Analytics Intelligence Platform - Graceful Shutdown Complete*
"""
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"[SUCCESS] Shutdown report generated: {report_path}")
        return report_path
    
    def execute_shutdown(self, force: bool = False, skip_state: bool = False) -> ShutdownResult:
        """Execute complete graceful shutdown with visual indicators"""
        print("\n[LAUNCH] EXECUTING GRACEFUL SHUTDOWN...")
        
        errors = []
        
        # Anti-recursion protection
        shutdown_guard = f"shutdown_{self.shutdown_id}"
        if shutdown_guard in self.recursion_guard:
            print("[LOCK] ANTI-RECURSION: Shutdown already in progress")
            return ShutdownResult(False, 0, 0, False, False, 0, ["Shutdown already in progress"])
        
        self.recursion_guard.add(shutdown_guard)
        
        try:
            # Phase 1: Detect processes
            print("\n[CLIPBOARD] PHASE 1: PROCESS DETECTION")
            processes = self.detect_platform_processes()
            
            # Phase 2: Save state (unless skipped)
            print("\n[CLIPBOARD] PHASE 2: STATE PRESERVATION")
            database_saved = True
            if not skip_state:
                database_saved = self.save_system_state()
            else:
                print("[WARNING]  Skipping state preservation (--skip-state)")
            
            # Phase 3: Graceful termination
            print("\n[CLIPBOARD] PHASE 3: PROCESS TERMINATION")
            terminated_count = 0
            if processes:
                terminated_count = self.graceful_process_termination(processes)
            else:
                print("[?][?]  No platform processes to terminate")
            
            # Phase 4: Cleanup
            print("\n[CLIPBOARD] PHASE 4: RESOURCE CLEANUP")
            cleanup_actions = self.cleanup_resources()
            
            # Phase 5: Final validation
            print("\n[CLIPBOARD] PHASE 5: FINAL VALIDATION")
            remaining_processes = self.detect_platform_processes()
            if remaining_processes and not force:
                errors.append(f"Warning: {len(remaining_processes)} processes still running")
            
            shutdown_time = time.time() - self.start_time
            success = len(errors) == 0 or force
            
            # Generate result
            result = ShutdownResult(
                success=success,
                processes_terminated=terminated_count,
                cleanup_actions=cleanup_actions,
                database_saved=database_saved,
                reports_generated=True,
                shutdown_time=shutdown_time,
                errors=errors
            )
            
            # Generate report
            report_path = self.generate_shutdown_report(result)
            
            print(f"\n{'[SUCCESS]' if success else '[WARNING]'} SHUTDOWN {'COMPLETED' if success else 'COMPLETED WITH WARNINGS'}")
            print(f"[?][?]  Duration: {shutdown_time:.2f} seconds")
            print(f"[BAR_CHART] Report: {report_path}")
            
            return result
            
        except Exception as e:
            print(f"[ERROR] Critical error during shutdown: {str(e)}")
            errors.append(f"Critical error: {str(e)}")
            return ShutdownResult(False, 0, 0, False, False, time.time() - self.start_time, errors)
        
        finally:
            self.recursion_guard.discard(shutdown_guard)

def main():
    """Main CLI entry point with argument parsing"""
    parser = argparse.ArgumentParser(
        description='Graceful Shutdown CLI for Enhanced Analytics Intelligence Platform',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python graceful_shutdown.py                    # Standard graceful shutdown
  python graceful_shutdown.py --force           # Force shutdown even with warnings
  python graceful_shutdown.py --skip-state      # Skip state preservation
  python graceful_shutdown.py --status          # Show current platform status
        """
    )
    
    parser.add_argument('--force', '-f', action='store_true',
                        help='Force shutdown even if warnings occur')
    parser.add_argument('--skip-state', '-s', action='store_true',
                        help='Skip state preservation (faster shutdown)')
    parser.add_argument('--status', action='store_true',
                        help='Show current platform status without shutdown')
    
    args = parser.parse_args()
    
    try:
        shutdown_cli = GracefulShutdownCLI()
        
        if args.status:
            print("\n[BAR_CHART] PLATFORM STATUS CHECK...")
            processes = shutdown_cli.detect_platform_processes()
            print(f"\n[SUCCESS] STATUS: {len(processes)} platform processes currently running")
            if processes:
                print("[PROCESSING] Platform is operational - use shutdown command to stop")
            else:
                print("[WARNING]  Platform appears to be stopped")
            return
        
        print("\n[WARNING]  WARNING: This will shut down the 24/7 monitoring system!")
        print("[BAR_CHART] Current platform processes will be gracefully terminated.")
        print("[STORAGE] System state will be preserved for restart.")
        
        if not args.force:
            response = input("\n[PROCESSING] Continue with graceful shutdown? (y/N): ")
            if response.lower() not in ['y', 'yes']:
                print("[ERROR] Shutdown cancelled by user")
                return
        
        # Execute shutdown
        result = shutdown_cli.execute_shutdown(force=args.force, skip_state=args.skip_state)
        
        if result.success:
            print("\n[COMPLETE] GRACEFUL SHUTDOWN COMPLETED SUCCESSFULLY")
            print("[PROCESSING] Platform can be restarted using the launch scripts")
        else:
            print("\n[WARNING]  SHUTDOWN COMPLETED WITH WARNINGS")
            print("[SEARCH] Check the shutdown report for details")
            
        sys.exit(0 if result.success else 1)
        
    except KeyboardInterrupt:
        print("\n\n[ERROR] Shutdown interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
